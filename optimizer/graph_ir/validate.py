"""CLI для валидации Graph IR v0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.graph_ir.io import GraphIRLoadError, GraphIRSpecValidationError, load_graph_ir_spec


class GraphIRValidateCli:
    """Компонент CLI-валидации Graph IR спецификаций."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает парсер аргументов CLI."""

        parser = argparse.ArgumentParser(description="Валидатор Graph IR v0")
        parser.add_argument("--file", required=True, help="Путь до Graph IR JSON-файла.")
        parser.add_argument("--pretty", action="store_true", help="Печатать summary в pretty JSON.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает CLI-валидацию и возвращает код завершения."""

        parser = GraphIRValidateCli.build_parser()
        args = parser.parse_args(argv)
        file_path = Path(args.file).resolve()
        try:
            spec = load_graph_ir_spec(file_path)
        except (GraphIRLoadError, GraphIRSpecValidationError) as exc:
            print(f"[GRAPH_IR INVALID] {exc}", file=sys.stderr)
            return 1

        summary = spec.summary()
        if args.pretty:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False))
        return 0


def main() -> None:
    """Точка входа для запуска `python -m optimizer.graph_ir.validate`."""

    raise SystemExit(GraphIRValidateCli.run())


if __name__ == "__main__":
    main()

