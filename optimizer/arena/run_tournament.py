"""CLI запуска турнира Architecture Arena v0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.arena.io import ArenaLoadError, ArenaValidationError, load_arena_tournament_spec
from optimizer.arena.runner import ArchitectureArenaRunner
from optimizer.common.env_loader import load_env_file


class ArenaRunCli:
    """CLI-компонент запуска турнира архитектур."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов запуска Arena турнира."""

        parser = argparse.ArgumentParser(description="Architecture Arena equal-budget tournament v0")
        parser.add_argument("--arena-file", required=True, help="Путь до YAML-конфига турнира Arena.")
        parser.add_argument("--details", action="store_true", help="Включить подробный oracle-отчет участников.")
        parser.add_argument("--pretty", action="store_true", help="Печатать JSON в pretty-формате.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает турнир Arena и возвращает код завершения CLI."""

        parser = ArenaRunCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        load_env_file(project_root / ".env")

        arena_file = Path(args.arena_file).resolve()
        try:
            spec = load_arena_tournament_spec(arena_file)
            runner = ArchitectureArenaRunner()
            result = runner.run(spec=spec, arena_file_dir=arena_file.parent, include_details=args.details)
        except (ArenaLoadError, ArenaValidationError, ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"[ARENA ERROR] {exc}", file=sys.stderr)
            return 1

        payload = result.to_payload()
        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))
        return 0


def main() -> None:
    """Точка входа для `python -m optimizer.arena.run_tournament`."""

    raise SystemExit(ArenaRunCli.run())


if __name__ == "__main__":
    main()

