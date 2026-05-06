"""CLI запуска executable oracle runner по golden dataset и DSL/IR workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from optimizer.common.env_loader import load_env_file
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.evaluation.dataset_loader import GoldenDatasetLoader
from optimizer.evaluation.dataset_schema import GoldenDatasetRecord
from optimizer.evaluation.oracle_runner import OracleRunner
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer
from optimizer.renderer.langgraph_dai.run import _build_demo_bindings


class OracleRunCli:
    """CLI-компонент oracle-прогона на golden dataset."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов запуска oracle runner."""

        parser = argparse.ArgumentParser(description="Executable oracle runner for golden dataset")
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument("--dsl-file", default="", help="Путь до DSL YAML файла.")
        source_group.add_argument("--graph-ir-file", default="", help="Путь до Graph IR JSON файла.")
        parser.add_argument("--dataset-file", required=True, help="Путь до golden dataset JSONL.")
        parser.add_argument("--task-prefix", default="oracle-task", help="Префикс task_id для кейсов прогона.")
        parser.add_argument(
            "--execution-mode",
            default="expected_stub",
            choices=["expected_stub", "runtime"],
            help="Режим исполнения кейсов: deterministic stub или реальный runtime.",
        )
        parser.add_argument("--details", action="store_true", help="Печатать полный отчет по кейсам.")
        parser.add_argument("--pretty", action="store_true", help="Печатать JSON в pretty-формате.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает oracle runner и возвращает код завершения."""

        parser = OracleRunCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        load_env_file(project_root / ".env")

        dataset_loader = GoldenDatasetLoader()
        dataset_result = dataset_loader.load_file(Path(args.dataset_file))
        if not dataset_result.is_success:
            for issue in dataset_result.issues:
                print(f"[ORACLE DATASET ERROR] line={issue.line_number}: {issue.message}", file=sys.stderr)
            return 1

        execute_fn = _build_execute_fn(args)
        runner = OracleRunner()
        run_result = runner.run(dataset_result.records, execute_fn)
        payload = run_result.full_payload() if args.details else run_result.summary_payload()
        payload["execution_mode"] = args.execution_mode
        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))
        return 0 if run_result.failed == 0 else 1


def _build_execute_fn(args: argparse.Namespace):
    """Строит функцию исполнения кейса в выбранном режиме."""

    if args.execution_mode == "expected_stub":
        return _execute_expected_stub

    graph_ir = _resolve_graph_ir(args)
    renderer = GraphIRToLangGraphRenderer()
    runtime = renderer.render(graph_ir=graph_ir, bindings=_build_demo_bindings())

    def _execute_runtime(record: GoldenDatasetRecord) -> dict[str, Any]:
        """Выполняет один кейс через реальный runtime workflow."""

        task_id = f"{args.task_prefix}-{record.case_id}"
        state = runtime.invoke(payload=record.input, task_id=task_id)
        return {
            "text": _extract_text_from_state(state),
            "payload": state.payload,
            "node_outputs": state.node_outputs,
        }

    return _execute_runtime


def _execute_expected_stub(record: GoldenDatasetRecord) -> dict[str, Any]:
    """Детерминированный executor для smoke/CI: строит текст из expected.must_include."""

    must_include = record.expected.get("must_include")
    parts = [item for item in must_include if isinstance(item, str)] if isinstance(must_include, list) else []
    if not parts:
        parts = [f"stub-answer-{record.case_id}"]
    text = ". ".join(parts)
    return {"text": text}


def _resolve_graph_ir(args: argparse.Namespace):
    """Разрешает Graph IR напрямую или через компиляцию DSL."""

    if args.graph_ir_file:
        return load_graph_ir_spec(Path(args.graph_ir_file).resolve())
    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(Path(args.dsl_file).resolve())
    if compile_result.graph_ir is None:
        raise ValueError(f"Не удалось скомпилировать DSL: {compile_result.report.summary()}")
    return compile_result.graph_ir


def _extract_text_from_state(state: Any) -> str:
    """Извлекает основной текст ответа из runtime state."""

    payload = getattr(state, "payload", {})
    if isinstance(payload, dict):
        text = payload.get("text")
        if isinstance(text, str):
            return text
    return str(payload)


def main() -> None:
    """Точка входа для `python -m optimizer.evaluation.run_oracle`."""

    raise SystemExit(OracleRunCli.run())


if __name__ == "__main__":
    main()
