"""CLI генерации исполняемого кода агента из DSL или Graph IR."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from optimizer.codegen.agent_generator import AgentCodeGenerator, sanitize_package_name
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.compile_report import CompileStatus
from optimizer.graph_ir.io import load_graph_ir_spec


class AgentCodegenCli:
    """CLI-компонент генерации Python-агента для найденной конфигурации."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов генерации агента."""

        parser = argparse.ArgumentParser(description="Генерация исполняемого кода агента AutoAgent Optimizer")
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument("--dsl-file", default="", help="Путь до DSL YAML файла.")
        source_group.add_argument("--graph-ir-file", default="", help="Путь до Graph IR JSON файла.")
        parser.add_argument("--output-dir", required=True, help="Каталог, куда сохранить сгенерированный агент.")
        parser.add_argument(
            "--package-name",
            default="",
            help="Имя Python-пакета агента. Если не передано, формируется автоматически.",
        )
        parser.add_argument("--force", action="store_true", help="Перезаписать существующий каталог пакета.")
        parser.add_argument("--pretty", action="store_true", help="Печатать результат в pretty JSON.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Выполняет генерацию агента и возвращает код завершения."""

        parser = AgentCodegenCli.build_parser()
        args = parser.parse_args(argv)

        graph_ir, source_name = _resolve_graph_ir_and_name(args)
        package_name = _resolve_package_name(args.package_name, source_name)

        generator = AgentCodeGenerator()
        try:
            result = generator.generate(
                graph_ir=graph_ir,
                output_dir=Path(args.output_dir).resolve(),
                package_name=package_name,
                force=args.force,
            )
        except ValueError as exc:
            print(f"[AGENT CODEGEN ERROR] {exc}", file=sys.stderr)
            return 1

        summary = result.summary()
        if args.pretty:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False))
        return 0


def _resolve_graph_ir_and_name(args: argparse.Namespace):
    """Разрешает Graph IR и базовое имя источника для package naming."""

    if args.graph_ir_file:
        graph_ir_path = Path(args.graph_ir_file).resolve()
        graph_ir = load_graph_ir_spec(graph_ir_path)
        return graph_ir, graph_ir_path.stem

    dsl_path = Path(args.dsl_file).resolve()
    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(dsl_path)
    if compile_result.report.status == CompileStatus.FAILURE or compile_result.graph_ir is None:
        for issue in compile_result.report.issues:
            if issue.severity.value == "error":
                print(f"[AGENT CODEGEN ERROR] {issue.message}", file=sys.stderr)
        raise ValueError("Не удалось скомпилировать DSL в Graph IR.")
    return compile_result.graph_ir, dsl_path.stem


def _resolve_package_name(raw_package_name: str, source_name: str) -> str:
    """Определяет финальное имя пакета агента."""

    if raw_package_name.strip():
        return sanitize_package_name(raw_package_name)
    normalized_source = re.sub(r"[^a-zA-Z0-9_]+", "_", source_name).strip("_")
    candidate = f"{normalized_source}_agent" if normalized_source else "generated_agent"
    return sanitize_package_name(candidate)


def main() -> None:
    """Точка входа для `python -m optimizer.codegen.generate`."""

    raise SystemExit(AgentCodegenCli.run())


if __name__ == "__main__":
    main()

