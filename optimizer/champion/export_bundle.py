"""CLI экспорта champion bundle v0 из результатов Arena турнира."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from optimizer.arena.io import ArenaLoadError, ArenaValidationError, load_arena_tournament_spec
from optimizer.arena.runner import ArchitectureArenaRunner
from optimizer.champion.diagnostic_map import DiagnosticMapBuildError, build_diagnostic_map_payload
from optimizer.codegen.agent_generator import AgentCodeGenerator, sanitize_package_name
from optimizer.common.env_loader import load_env_file
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.compile_report import CompileStatus
from optimizer.evidence.pack_builder import (
    EvidencePackBuildError,
    build_evidence_pack_payload,
    render_evidence_markdown,
)
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec


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
    generated = AgentCodeGenerator().generate(
        graph_ir=winner_graph_ir,
        output_dir=generated_agent_dir,
        package_name=sanitize_package_name(f"{winner_id}_agent"),
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

    manifest_payload = {
        "version": "champion_bundle_v0",
        "winner_id": winner_id,
        "winner_source_kind": source_kind,
        "winner_source_file": str(copied_winner_source_file),
        "arena_result_file": str(arena_result_file),
        "diagnostic_map_file": str(diagnostic_map_file),
        "evidence_pack_json_file": str(evidence_json_file),
        "evidence_pack_markdown_file": str(evidence_md_file),
        "winner_graph_ir_file": str(winner_graph_ir_file),
        "generated_agent_dir": str(generated_agent_dir),
        "generated_agent_entrypoint_file": str(generated.entrypoint_file),
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
        "generated_agent_entrypoint_file": str(generated.entrypoint_file),
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


def main() -> None:
    """Точка входа для `python -m optimizer.champion.export_bundle`."""

    raise SystemExit(ChampionBundleCli.run())


if __name__ == "__main__":
    main()

