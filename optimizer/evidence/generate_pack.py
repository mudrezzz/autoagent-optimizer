"""CLI генерации Evidence Pack v0 из Arena-конфига или готового Arena JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from optimizer.arena.io import ArenaLoadError, ArenaValidationError, load_arena_tournament_spec
from optimizer.arena.runner import ArchitectureArenaRunner
from optimizer.common.env_loader import load_env_file
from optimizer.evidence.pack_builder import (
    EvidencePackBuildError,
    build_evidence_pack_payload,
    render_evidence_markdown,
)


class EvidencePackCli:
    """CLI-компонент генерации evidence pack по результатам tournament run."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов генерации evidence pack."""

        parser = argparse.ArgumentParser(description="Generate Evidence Pack v0 from Arena result")
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument("--arena-file", default="", help="Путь до Arena YAML конфигурации турнира.")
        source_group.add_argument(
            "--arena-result-file",
            default="",
            help="Путь до сохраненного JSON результата `optimizer.arena.run_tournament`.",
        )
        parser.add_argument(
            "--out-dir",
            default=".\\tmp\\evidence_pack",
            help="Каталог, куда сохранить evidence_pack.json и evidence_pack.md.",
        )
        parser.add_argument(
            "--include-details",
            action="store_true",
            help="Для --arena-file включает подробный oracle отчет участников (details=true).",
        )
        parser.add_argument("--pretty", action="store_true", help="Печатать итоговый JSON-ответ в pretty формате.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает генерацию evidence pack и возвращает CLI код завершения."""

        parser = EvidencePackCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        load_env_file(project_root / ".env")

        out_dir = Path(args.out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            arena_payload = _resolve_arena_payload(args)
            pack_payload = build_evidence_pack_payload(arena_payload)
        except (
            ArenaLoadError,
            ArenaValidationError,
            EvidencePackBuildError,
            ValueError,
            FileNotFoundError,
            json.JSONDecodeError,
        ) as exc:
            print(f"[EVIDENCE ERROR] {exc}", file=sys.stderr)
            return 1

        json_file = out_dir / "evidence_pack.json"
        markdown_file = out_dir / "evidence_pack.md"
        json_file.write_text(json.dumps(pack_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        markdown_file.write_text(render_evidence_markdown(pack_payload), encoding="utf-8")

        result_payload = {
            "status": "success",
            "version": "evidence_pack_v0",
            "evidence_json_file": str(json_file),
            "evidence_markdown_file": str(markdown_file),
            "winner_id": pack_payload.get("tournament", {}).get("winner_id"),
            "challenger_id": pack_payload.get("tournament", {}).get("challenger_id"),
        }
        if args.pretty:
            print(json.dumps(result_payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result_payload, ensure_ascii=False))
        return 0


def _resolve_arena_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Разрешает входные данные турнира: из YAML-конфига или из готового JSON файла."""

    if args.arena_result_file:
        payload_file = Path(args.arena_result_file).resolve()
        raw = payload_file.read_text(encoding="utf-8-sig")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("`--arena-result-file` должен содержать JSON объект.")
        return payload

    arena_file = Path(args.arena_file).resolve()
    spec = load_arena_tournament_spec(arena_file)
    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=arena_file.parent, include_details=bool(args.include_details))
    return result.to_payload()


def main() -> None:
    """Точка входа для `python -m optimizer.evidence.generate_pack`."""

    raise SystemExit(EvidencePackCli.run())


if __name__ == "__main__":
    main()

