"""CLI-команда компиляции DSL в Graph IR."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.compile_report import CompileStatus


class DslCompileCli:
    """Компонент CLI для компиляции DSL-файлов в Graph IR."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает парсер CLI-аргументов."""

        parser = argparse.ArgumentParser(description="Компилятор AutoAgent DSL v0 -> Graph IR v0")
        parser.add_argument("--dsl-file", required=True, help="Путь до исходного DSL YAML-файла.")
        parser.add_argument("--output-ir-file", default="", help="Путь, куда сохранить собранный Graph IR JSON.")
        parser.add_argument("--pretty", action="store_true", help="Печатать report summary в формате pretty JSON.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает компиляцию и возвращает код завершения."""

        parser = DslCompileCli.build_parser()
        args = parser.parse_args(argv)

        compiler = DslToGraphIRCompiler()
        dsl_path = Path(args.dsl_file).resolve()
        result = compiler.compile_file(dsl_path)

        summary = result.report.summary()
        if args.pretty:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False))

        if result.report.status == CompileStatus.FAILURE or result.graph_ir is None:
            for issue in result.report.issues:
                if issue.severity.value == "error":
                    print(f"[DSL COMPILE ERROR] {issue.message}", file=sys.stderr)
            return 1

        output_ir_file = args.output_ir_file.strip()
        if output_ir_file:
            output_path = Path(output_ir_file).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.graph_ir.model_dump_json(indent=2), encoding="utf-8")
            print(json.dumps({"output_ir_file": str(output_path)}, ensure_ascii=False))
        return 0


def main() -> None:
    """Точка входа для `python -m optimizer.dsl.compile`."""

    raise SystemExit(DslCompileCli.run())


if __name__ == "__main__":
    main()

