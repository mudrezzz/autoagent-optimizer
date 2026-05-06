"""CLI запуска и возобновления рендеренного workflow поверх Graph IR/DSL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from optimizer.common.env_loader import load_env_file
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer, RendererBindings
from optimizer.renderer.langgraph_dai.checkpoint_store import FileRuntimeCheckpointStore, RuntimeCheckpointStoreError
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState


class RendererRunCli:
    """CLI-компонент для запуска Graph IR workflow."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов запуска."""

        parser = argparse.ArgumentParser(description="Запуск/возобновление Graph IR workflow на базе langgraph-dai")
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument("--graph-ir-file", default="", help="Путь до Graph IR JSON файла.")
        source_group.add_argument("--dsl-file", default="", help="Путь до DSL YAML файла (с компиляцией перед запуском).")
        parser.add_argument("--payload-json", default="{}", help="JSON-объект входного payload или payload patch.")
        parser.add_argument("--payload-file", default="", help="Путь до JSON-файла payload или payload patch.")
        parser.add_argument("--task-id", default="demo-task", help="task_id для нового invoke-запуска.")
        parser.add_argument("--run-id", default="", help="run_id для трассировки; если пусто, генерируется автоматически.")
        parser.add_argument("--resume-task-id", default="", help="Если задан, выполняется resume из checkpoint по этому task_id.")
        parser.add_argument(
            "--checkpoint-dir",
            default=".\\tmp\\runtime_checkpoints",
            help="Каталог хранения checkpoint runtime-состояний.",
        )
        parser.add_argument(
            "--disable-langgraph-checkpointer",
            action="store_true",
            help="Отключает встроенный LangGraph checkpointer (для локальной диагностики).",
        )
        parser.add_argument("--pretty", action="store_true", help="Печатать результат в pretty JSON.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает workflow и возвращает код завершения."""

        parser = RendererRunCli.build_parser()
        args = parser.parse_args(argv)

        # Загружаем локальный `.env`, если существует.
        project_root = Path(__file__).resolve().parents[3]
        load_env_file(project_root / ".env")

        try:
            graph_ir = _resolve_graph_ir(args)
            payload = _resolve_payload(args)
            checkpoint_store = FileRuntimeCheckpointStore(Path(args.checkpoint_dir).resolve())
            renderer = GraphIRToLangGraphRenderer()
            runtime = renderer.render(
                graph_ir=graph_ir,
                bindings=_build_demo_bindings(),
                checkpoint_store=checkpoint_store,
                enable_langgraph_checkpointer=(not args.disable_langgraph_checkpointer),
            )

            if args.resume_task_id.strip():
                final_state = runtime.resume(
                    task_id=args.resume_task_id.strip(),
                    payload_patch=payload,
                    run_id=(args.run_id.strip() or None),
                )
            else:
                final_state = runtime.invoke(
                    payload=payload,
                    task_id=args.task_id,
                    run_id=(args.run_id.strip() or None),
                )
        except (ValueError, RuntimeCheckpointStoreError, FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"[RUNTIME ERROR] {exc}", file=sys.stderr)
            return 1

        rendered = _render_state_summary(final_state)
        if args.pretty:
            print(json.dumps(rendered, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(rendered, ensure_ascii=False))
        return 0


def _resolve_graph_ir(args: argparse.Namespace):
    """Определяет источник Graph IR: прямой файл или компиляция DSL."""

    if args.graph_ir_file:
        return load_graph_ir_spec(Path(args.graph_ir_file).resolve())

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(Path(args.dsl_file).resolve())
    if compile_result.graph_ir is None:
        raise ValueError(f"Не удалось скомпилировать DSL: {compile_result.report.summary()}")
    return compile_result.graph_ir


def _parse_payload_json(raw: str) -> dict[str, Any]:
    """Парсит payload JSON-строку в словарь."""

    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Аргумент --payload-json должен быть JSON-объектом.")
    return payload


def _resolve_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Разрешает payload либо из файла, либо из inline JSON."""

    if args.payload_file:
        payload_path = Path(args.payload_file).resolve()
        payload_raw = payload_path.read_text(encoding="utf-8-sig")
        return _parse_payload_json(payload_raw)
    return _parse_payload_json(args.payload_json)


def _render_state_summary(state: RenderedGraphState) -> dict[str, Any]:
    """Формирует компактное summary финального состояния workflow."""

    return {
        "run_id": state.task_context.get("run_id"),
        "task_id": state.task_context.get("task_id"),
        "executed_nodes": state.executed_nodes,
        "skipped_nodes": state.skipped_nodes,
        "errors": state.errors,
        "payload": state.payload,
        "node_outputs": state.node_outputs,
        "trace": state.trace,
        "node_events": state.node_events,
        "trace_summary": state.trace_summary,
    }


def _build_demo_bindings() -> RendererBindings:
    """Создает базовые биндинги для demo-примеров текущего этапа."""

    def _always_valid(_state: RenderedGraphState, _node) -> dict[str, Any]:
        """Универсальный validator для demo сценариев."""

        return {"valid": True}

    def _invoice_normalizer(state: RenderedGraphState, _node) -> dict[str, Any]:
        """Упрощенный deterministic normalizer для demo OCR-пайплайна."""

        query = state.payload.get("query", "")
        return {"normalized_text": str(query)}

    def _policy_validator(state: RenderedGraphState, _node) -> dict[str, Any]:
        """Validator, который пробрасывает action_risk для branch-логики."""

        action_risk = state.payload.get("action_risk", "low")
        return {"valid": True, "action_risk": action_risk}

    prompt_templates = {
        "support_answer_v1": "Ответь кратко и по делу на запрос пользователя: {query}",
        "invoice_repair_v1": "Исправь отсутствующие поля инвойса по тексту: {normalized_text}",
        "action_routing_v1": "Определи безопасный маршрут действия для запроса: {query}",
    }

    deterministic_registry = {
        "python://components.invoice_normalizer:normalize_invoice": _invoice_normalizer,
    }
    validator_registry = {
        "python://validators.support_schema_guard:validate": _always_valid,
        "python://validators.invoice_schema_guard:validate": _always_valid,
        "python://validators.policy_guard:validate_action": _policy_validator,
    }

    return RendererBindings(
        prompt_templates=prompt_templates,
        deterministic_registry=deterministic_registry,
        validator_registry=validator_registry,
    )


def main() -> None:
    """Точка входа для `python -m optimizer.renderer.langgraph_dai.run`."""

    raise SystemExit(RendererRunCli.run())


if __name__ == "__main__":
    main()

