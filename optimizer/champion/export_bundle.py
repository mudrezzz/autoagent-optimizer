"""CLI экспорта champion bundle v0 из результатов Arena турнира."""

from __future__ import annotations

import argparse
import contextlib
import os
import json
import re
import shutil
import sys
import importlib.util
from pathlib import Path
from typing import Any

from optimizer.arena.io import ArenaLoadError, ArenaValidationError, load_arena_tournament_spec
from optimizer.arena.runner import ArchitectureArenaRunner
from optimizer.champion.diagnostic_map import DiagnosticMapBuildError, build_diagnostic_map_payload
from optimizer.champion.native_export import NativeExportBuildError, NativeLanggraphDaiExporter
from optimizer.codegen.agent_generator import AgentCodeGenerator, sanitize_package_name
from optimizer.common.env_loader import load_env_file
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.compile_report import CompileStatus
from optimizer.evaluation.dataset_loader import GoldenDatasetLoader
from optimizer.evidence.pack_builder import (
    EvidencePackBuildError,
    build_evidence_pack_payload,
    render_evidence_markdown,
)
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer, RendererBindings
from optimizer.renderer.langgraph_dai.run import _build_demo_bindings


class ChampionBundleExportError(ValueError):
    """Ошибка формирования champion export bundle."""


class ChampionBundleCli:
    """CLI-компонент сборки champion export bundle v0."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов экспорта champion bundle."""

        parser = argparse.ArgumentParser(description="Export champion bundle v0 from Arena result")
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument("--arena-file", default="", help="Путь до Arena YAML конфигурации турнира.")
        source_group.add_argument(
            "--arena-result-file",
            default="",
            help="Путь до сохраненного JSON результата `optimizer.arena.run_tournament`.",
        )
        parser.add_argument(
            "--out-dir",
            default=".\\tmp\\champion_bundle",
            help="Каталог, где будет создан подкаталог bundle.",
        )
        parser.add_argument(
            "--bundle-name",
            default="champion_bundle_v0",
            help="Имя подкаталога bundle внутри --out-dir.",
        )
        parser.add_argument(
            "--include-details",
            action="store_true",
            help="Для --arena-file включает подробный oracle отчет участников (details=true).",
        )
        parser.add_argument("--force", action="store_true", help="Перезаписать существующий bundle-каталог.")
        parser.add_argument("--pretty", action="store_true", help="Печатать итоговый JSON-ответ в pretty формате.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Выполняет экспорт champion bundle и возвращает код завершения CLI."""

        parser = ChampionBundleCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        load_env_file(project_root / ".env")

        out_dir = Path(args.out_dir).resolve()
        bundle_name = _sanitize_bundle_name(args.bundle_name)
        bundle_dir = out_dir / bundle_name

        try:
            _prepare_bundle_dir(bundle_dir=bundle_dir, force=bool(args.force))
            arena_payload, arena_input_file = _resolve_arena_payload(args)
            export_payload = _build_bundle(
                bundle_dir=bundle_dir,
                arena_payload=arena_payload,
                arena_input_file=arena_input_file,
            )
        except (
            ArenaLoadError,
            ArenaValidationError,
            ChampionBundleExportError,
            DiagnosticMapBuildError,
            NativeExportBuildError,
            EvidencePackBuildError,
            ValueError,
            FileNotFoundError,
            json.JSONDecodeError,
        ) as exc:
            print(f"[CHAMPION EXPORT ERROR] {exc}", file=sys.stderr)
            return 1

        if args.pretty:
            print(json.dumps(export_payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(export_payload, ensure_ascii=False))
        return 0


def _sanitize_bundle_name(raw_name: str) -> str:
    """Нормализует имя bundle-каталога для безопасного файлового пути."""

    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw_name.strip())
    normalized = normalized.strip("._-")
    return normalized or "champion_bundle_v0"


def _prepare_bundle_dir(*, bundle_dir: Path, force: bool) -> None:
    """Подготавливает каталог bundle, удаляя старую версию при `force=true`."""

    if bundle_dir.exists():
        if not force:
            raise ChampionBundleExportError(
                f"Каталог bundle уже существует: {bundle_dir}. Используйте --force для перезаписи."
            )
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)


def _resolve_arena_payload(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    """Разрешает входные данные турнира из Arena YAML или сохраненного Arena JSON."""

    if args.arena_result_file:
        arena_input_file = Path(args.arena_result_file).resolve()
        raw = arena_input_file.read_text(encoding="utf-8-sig")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ChampionBundleExportError("`--arena-result-file` должен содержать JSON объект.")
        return payload, arena_input_file

    arena_input_file = Path(args.arena_file).resolve()
    spec = load_arena_tournament_spec(arena_input_file)
    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=arena_input_file.parent, include_details=bool(args.include_details))
    return result.to_payload(), arena_input_file


def _build_bundle(
    *,
    bundle_dir: Path,
    arena_payload: dict[str, Any],
    arena_input_file: Path,
) -> dict[str, Any]:
    """Собирает все артефакты champion bundle и возвращает summary payload."""

    winner_participant = _resolve_winner_participant(arena_payload)
    winner_id = str(winner_participant.get("participant_id", ""))
    source_kind = str(winner_participant.get("source_kind", ""))
    source_path = Path(str(winner_participant.get("source_path", ""))).resolve()
    if not source_path.exists():
        raise ChampionBundleExportError(f"Файл winner-источника не найден: {source_path}")

    arena_result_file = bundle_dir / "arena_result.json"
    arena_result_file.write_text(json.dumps(arena_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    inputs_dir = bundle_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    copied_input_file = inputs_dir / arena_input_file.name
    shutil.copy2(arena_input_file, copied_input_file)

    winner_source_dir = bundle_dir / "winner_source"
    winner_source_dir.mkdir(parents=True, exist_ok=True)
    copied_winner_source_file = winner_source_dir / source_path.name
    shutil.copy2(source_path, copied_winner_source_file)

    winner_graph_ir = _resolve_winner_graph_ir(source_kind=source_kind, source_path=source_path, winner_id=winner_id)
    winner_graph_ir_file = bundle_dir / "winner_graph_ir.json"
    winner_graph_ir_file.write_text(winner_graph_ir.model_dump_json(indent=2), encoding="utf-8")

    generated_agent_dir = bundle_dir / "generated_agent"
    demo_bindings = _build_demo_bindings()
    generated = AgentCodeGenerator().generate(
        graph_ir=winner_graph_ir,
        output_dir=generated_agent_dir,
        package_name=sanitize_package_name(f"{winner_id}_agent"),
        force=True,
        prompt_templates_override=demo_bindings.prompt_templates,
    )

    native_agent_dir = bundle_dir / "native_agent"
    native_export_result = NativeLanggraphDaiExporter().export(
        graph_ir=winner_graph_ir,
        prompt_templates=demo_bindings.prompt_templates,
        output_dir=native_agent_dir,
        force=True,
    )

    evidence_payload = build_evidence_pack_payload(arena_payload)
    evidence_json_file = bundle_dir / "evidence_pack.json"
    evidence_md_file = bundle_dir / "evidence_pack.md"
    evidence_json_file.write_text(json.dumps(evidence_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    evidence_md_file.write_text(render_evidence_markdown(evidence_payload), encoding="utf-8")

    diagnostic_map_payload = build_diagnostic_map_payload(arena_payload)
    diagnostic_map_file = bundle_dir / "diagnostic_map.json"
    diagnostic_map_file.write_text(json.dumps(diagnostic_map_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    parity_payload = _resolve_parity_payload(arena_payload)
    parity_report_payload = _build_parity_report(
        winner_id=winner_id,
        winner_graph_ir=winner_graph_ir,
        source_kind=source_kind,
        generated_package_dir=generated.package_dir,
        native_agent_dir=native_export_result.output_dir,
        parity_payload=parity_payload,
    )
    parity_report_file = bundle_dir / "parity_report.json"
    parity_report_file.write_text(json.dumps(parity_report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    bundle_readme_file = bundle_dir / "README.bundle.md"
    bundle_readme_file.write_text(
        _render_bundle_readme(
            winner_id=winner_id,
            winner_source_kind=source_kind,
            winner_source_file=copied_winner_source_file,
            generated_entrypoint_file=generated.entrypoint_file,
            native_entrypoint_file=native_export_result.run_file,
            parity_report_file=parity_report_file,
        ),
        encoding="utf-8",
    )

    manifest_payload = {
        "version": "champion_bundle_v0",
        "winner_id": winner_id,
        "winner_source_kind": source_kind,
        "winner_source_file": str(copied_winner_source_file),
        "arena_result_file": str(arena_result_file),
        "diagnostic_map_file": str(diagnostic_map_file),
        "evidence_pack_json_file": str(evidence_json_file),
        "evidence_pack_markdown_file": str(evidence_md_file),
        "parity_report_file": str(parity_report_file),
        "bundle_readme_file": str(bundle_readme_file),
        "winner_graph_ir_file": str(winner_graph_ir_file),
        "generated_agent_dir": str(generated_agent_dir),
        "generated_agent_entrypoint_file": str(generated.entrypoint_file),
        "native_agent_dir": str(native_export_result.output_dir),
        "native_agent_entrypoint_file": str(native_export_result.run_file),
    }
    manifest_file = bundle_dir / "bundle_manifest.json"
    manifest_file.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "success",
        "version": "champion_bundle_v0",
        "bundle_dir": str(bundle_dir),
        "winner_id": winner_id,
        "manifest_file": str(manifest_file),
        "diagnostic_map_file": str(diagnostic_map_file),
        "evidence_pack_json_file": str(evidence_json_file),
        "evidence_pack_markdown_file": str(evidence_md_file),
        "parity_report_file": str(parity_report_file),
        "bundle_readme_file": str(bundle_readme_file),
        "generated_agent_entrypoint_file": str(generated.entrypoint_file),
        "native_agent_entrypoint_file": str(native_export_result.run_file),
    }


def _resolve_winner_participant(arena_payload: dict[str, Any]) -> dict[str, Any]:
    """Находит payload winner-участника по `winner_id` в списке `participants`."""

    winner_id = str(arena_payload.get("winner_id", ""))
    participants = arena_payload.get("participants", [])
    if not winner_id:
        raise ChampionBundleExportError("В Arena payload отсутствует `winner_id`.")
    if not isinstance(participants, list):
        raise ChampionBundleExportError("В Arena payload поле `participants` должно быть списком.")

    for participant in participants:
        if not isinstance(participant, dict):
            continue
        if str(participant.get("participant_id", "")) == winner_id:
            source_kind = str(participant.get("source_kind", ""))
            source_path = str(participant.get("source_path", ""))
            if source_kind not in {"dsl", "graph_ir"}:
                raise ChampionBundleExportError(
                    f"У winner `{winner_id}` отсутствует корректный source_kind (ожидается dsl|graph_ir)."
                )
            if not source_path:
                raise ChampionBundleExportError(f"У winner `{winner_id}` отсутствует `source_path`.")
            return participant

    raise ChampionBundleExportError(f"Winner `{winner_id}` не найден в participants.")


def _resolve_winner_graph_ir(*, source_kind: str, source_path: Path, winner_id: str) -> GraphIRSpec:
    """Разрешает Graph IR winner: напрямую из JSON или через компиляцию DSL."""

    if source_kind == "graph_ir":
        return load_graph_ir_spec(source_path)

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(source_path)
    if compile_result.report.status == CompileStatus.FAILURE or compile_result.graph_ir is None:
        raise ChampionBundleExportError(
            f"Не удалось скомпилировать DSL winner `{winner_id}` в Graph IR: {compile_result.report.summary()}"
        )
    return compile_result.graph_ir


def _resolve_parity_payload(arena_payload: dict[str, Any]) -> dict[str, Any]:
    """Подбирает payload для parity-run из dataset файла или возвращает fallback."""

    dataset_file = arena_payload.get("dataset_file")
    if not isinstance(dataset_file, str) or not dataset_file.strip():
        return {"query": "Parity check payload"}

    try:
        loader = GoldenDatasetLoader()
        result = loader.load_file(Path(dataset_file).resolve())
    except (FileNotFoundError, ValueError):
        return {"query": "Parity check payload"}

    if not result.records:
        return {"query": "Parity check payload"}
    sample_input = result.records[0].input
    if isinstance(sample_input, dict):
        return dict(sample_input)
    return {"query": "Parity check payload"}


def _build_parity_report(
    *,
    winner_id: str,
    winner_graph_ir: GraphIRSpec,
    source_kind: str,
    generated_package_dir: Path,
    native_agent_dir: Path,
    parity_payload: dict[str, Any],
) -> dict[str, Any]:
    """Строит parity-report между DSL path и generated-code path в mock-LLM режиме."""

    graph_ir_same = _is_graph_ir_same(winner_graph_ir=winner_graph_ir, generated_package_dir=generated_package_dir)
    runtime_comparison = _compare_runtime_paths(
        winner_graph_ir=winner_graph_ir,
        generated_package_dir=generated_package_dir,
        parity_payload=parity_payload,
    )
    native_runtime_comparison = _compare_native_runtime_path(
        native_agent_dir=native_agent_dir,
        parity_payload=parity_payload,
    )
    return {
        "version": "parity_report_v0",
        "winner_id": winner_id,
        "winner_source_kind": source_kind,
        "mode": "mock_llm_for_stability",
        "payload_used": parity_payload,
        "graph_ir_equivalent": graph_ir_same,
        "runtime_structural_parity": runtime_comparison,
        "native_runtime_smoke": native_runtime_comparison,
        "is_equivalent_agent": bool(
            graph_ir_same and runtime_comparison.get("passed", False) and native_runtime_comparison.get("passed", False)
        ),
        "notes": [
            "Проверка выполняется в mock LLM режиме для стабильности CI и исключения вариативности ответов модели.",
            "Для live LLM допускаются различия в `payload.text`, но не в структуре исполнения.",
            "Native runtime smoke подтверждает, что standalone export запускается отдельно от optimizer runtime.",
        ],
    }


def _is_graph_ir_same(*, winner_graph_ir: GraphIRSpec, generated_package_dir: Path) -> bool:
    """Проверяет, что winner Graph IR совпадает с graph_ir внутри generated package."""

    generated_graph_ir_file = generated_package_dir / "graph_ir.json"
    if not generated_graph_ir_file.exists():
        return False
    try:
        generated_graph_ir = load_graph_ir_spec(generated_graph_ir_file)
    except (ValueError, FileNotFoundError, json.JSONDecodeError):
        return False
    return winner_graph_ir.model_dump() == generated_graph_ir.model_dump()


def _compare_runtime_paths(
    *,
    winner_graph_ir: GraphIRSpec,
    generated_package_dir: Path,
    parity_payload: dict[str, Any],
) -> dict[str, Any]:
    """Сравнивает структурный runtime результат DSL-path и generated-code path."""

    dsl_bindings = _build_demo_bindings()
    generated_bindings = _load_generated_bindings(generated_package_dir)

    with _without_openrouter_api_key():
        renderer = GraphIRToLangGraphRenderer()
        dsl_runtime = renderer.render(graph_ir=winner_graph_ir, bindings=dsl_bindings)
        code_runtime = renderer.render(graph_ir=winner_graph_ir, bindings=generated_bindings)

        dsl_state = dsl_runtime.invoke(payload=dict(parity_payload), task_id="parity-dsl")
        code_state = code_runtime.invoke(payload=dict(parity_payload), task_id="parity-codegen")

    checks = {
        "executed_nodes_equal": dsl_state.executed_nodes == code_state.executed_nodes,
        "skipped_nodes_equal": dsl_state.skipped_nodes == code_state.skipped_nodes,
        "node_output_keys_equal": sorted(dsl_state.node_outputs.keys()) == sorted(code_state.node_outputs.keys()),
        "errors_equal": dsl_state.errors == code_state.errors,
        "trace_nodes_total_equal": (
            (dsl_state.trace_summary or {}).get("nodes_total") == (code_state.trace_summary or {}).get("nodes_total")
        ),
    }

    dsl_text = _resolve_payload_text(dsl_state.payload)
    code_text = _resolve_payload_text(code_state.payload)
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "dsl_output_text_sample": dsl_text[:500],
        "generated_output_text_sample": code_text[:500],
        "text_equal": dsl_text == code_text,
    }


def _compare_native_runtime_path(*, native_agent_dir: Path, parity_payload: dict[str, Any]) -> dict[str, Any]:
    """Проверяет запуск standalone native runtime-агента из экспортного bundle."""

    run_file = native_agent_dir / "app" / "run.py"
    if not run_file.exists():
        return {"passed": False, "error": f"native run file not found: {run_file}"}

    payload_file = native_agent_dir / "tmp_parity_payload.json"
    payload_file.write_text(json.dumps(parity_payload, ensure_ascii=False), encoding="utf-8")

    import subprocess

    proc = subprocess.run(
        [sys.executable, str(run_file), "--payload-file", str(payload_file), "--pretty"],
        capture_output=True,
        text=True,
        cwd=native_agent_dir,
        check=False,
    )
    payload_file.unlink(missing_ok=True)

    if proc.returncode != 0:
        return {"passed": False, "returncode": proc.returncode, "stderr": proc.stderr[-1000:]}
    try:
        output_payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"passed": False, "error": "native runner output is not valid JSON"}

    has_required_keys = all(
        key in output_payload for key in ("executed_nodes", "skipped_nodes", "errors", "payload", "node_outputs")
    )
    if not has_required_keys:
        return {"passed": False, "error": "native runner output misses required keys", "output": output_payload}
    return {
        "passed": True,
        "executed_nodes_total": len(output_payload.get("executed_nodes", [])),
        "errors_total": len(output_payload.get("errors", [])),
    }


def _load_generated_bindings(generated_package_dir: Path) -> RendererBindings:
    """Загружает RendererBindings из сгенерированного `bindings.py`."""

    bindings_file = generated_package_dir / "bindings.py"
    if not bindings_file.exists():
        raise ChampionBundleExportError(f"В generated package отсутствует файл bindings.py: {bindings_file}")

    module_name = f"_generated_bindings_{sanitize_package_name(generated_package_dir.name)}"
    module_spec = importlib.util.spec_from_file_location(module_name, bindings_file)
    if module_spec is None or module_spec.loader is None:
        raise ChampionBundleExportError(f"Не удалось загрузить generated bindings module: {bindings_file}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    build_bindings = getattr(module, "build_bindings", None)
    if not callable(build_bindings):
        raise ChampionBundleExportError("В generated bindings отсутствует callable `build_bindings()`.")
    bindings = build_bindings()
    if not isinstance(bindings, RendererBindings):
        raise ChampionBundleExportError("`build_bindings()` должен возвращать RendererBindings.")
    return bindings


@contextlib.contextmanager
def _without_openrouter_api_key():
    """Временно отключает OPENROUTER_API_KEY, чтобы parity-проверка была детерминированной."""

    previous = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = ""
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("OPENROUTER_API_KEY", None)
        else:
            os.environ["OPENROUTER_API_KEY"] = previous


def _resolve_payload_text(payload: Any) -> str:
    """Извлекает текст результата из payload или возвращает пустую строку."""

    if not isinstance(payload, dict):
        return ""
    text = payload.get("text")
    if isinstance(text, str):
        return text
    return ""


def _render_bundle_readme(
    *,
    winner_id: str,
    winner_source_kind: str,
    winner_source_file: Path,
    generated_entrypoint_file: Path,
    native_entrypoint_file: Path,
    parity_report_file: Path,
) -> str:
    """Рендерит README для разработчика по запуску и проверке champion bundle."""

    return (
        "# Champion Bundle README\n\n"
        f"- winner_id: `{winner_id}`\n"
        f"- winner_source_kind: `{winner_source_kind}`\n"
        f"- winner_source_file: `{winner_source_file}`\n\n"
        "## 1) Запуск сгенерированного агента\n\n"
        "```powershell\n"
        "New-Item -ItemType Directory -Force -Path .\\tmp | Out-Null\n"
        "'{\"draft_post\":\"Тестовый пост для проверки champion bundle\"}' | "
        "Set-Content -LiteralPath .\\tmp\\bundle_payload.json -Encoding UTF8\n"
        f"python {generated_entrypoint_file} --payload-file .\\tmp\\bundle_payload.json --pretty\n"
        "```\n\n"
        "## 1.1) Запуск standalone native-агента (`langgraph-dai`)\n\n"
        "```powershell\n"
        "New-Item -ItemType Directory -Force -Path .\\tmp | Out-Null\n"
        "'{\"draft_post\":\"Тестовый пост для проверки native bundle\"}' | "
        "Set-Content -LiteralPath .\\tmp\\native_payload.json -Encoding UTF8\n"
        f"python {native_entrypoint_file} --payload-file .\\tmp\\native_payload.json --pretty\n"
        "```\n\n"
        "## 2) Эквивалентность к DSL-path\n\n"
        "В bundle уже сохранен `parity_report.json` с автоматической проверкой:\n"
        "1. `graph_ir_equivalent=true` — Graph IR в generated package совпадает с winner Graph IR.\n"
        "2. `runtime_structural_parity.passed=true` — совпадает структура выполнения "
        "(executed/skipped nodes, node outputs keys, errors, trace nodes total).\n\n"
        "3. `native_runtime_smoke.passed=true` — standalone native runtime пакет реально запускается.\n\n"
        "Проверить отчет:\n\n"
        "```powershell\n"
        f"Get-Content -LiteralPath {parity_report_file}\n"
        "```\n\n"
        "Важно: `payload.text` может отличаться в live LLM режиме. Для этого parity check выполняется "
        "в mock LLM режиме и оценивает структурную эквивалентность исполнения.\n"
    )


def main() -> None:
    """Точка входа для `python -m optimizer.champion.export_bundle`."""

    raise SystemExit(ChampionBundleCli.run())


if __name__ == "__main__":
    main()
