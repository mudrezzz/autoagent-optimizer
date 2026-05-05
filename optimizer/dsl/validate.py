"""CLI для smoke-валидации DSL v0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.dsl.io import DslLoadError, DslValidationError, load_dsl_spec


class DslValidateCli:
    """Компонент CLI-валидации DSL спецификаций."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает argparse-парсер для запуска CLI-команды."""

        parser = argparse.ArgumentParser(description="Валидатор AutoAgent DSL v0")
        parser.add_argument(
            "--file",
            required=True,
            help="Путь до YAML DSL-файла.",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Печатать резюме в pretty-JSON формате.",
        )
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает CLI и возвращает код завершения процесса."""

        parser = DslValidateCli.build_parser()
        args = parser.parse_args(argv)

        file_path = Path(args.file).resolve()
        try:
            spec = load_dsl_spec(file_path)
        except (DslLoadError, DslValidationError) as exc:
            print(f"[DSL INVALID] {exc}", file=sys.stderr)
            return 1

        summary = spec.summary()
        if args.pretty:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False))
        return 0


def main() -> None:
    """Точка входа для `python -m optimizer.dsl.validate`."""

    raise SystemExit(DslValidateCli.run())


if __name__ == "__main__":
    main()

