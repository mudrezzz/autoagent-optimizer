"""CLI запуска profile-driven оценки задачи (Evaluation Profile v0)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.common.env_loader import load_env_file
from optimizer.evaluation.profile_io import (
    EvaluationProfileLoadError,
    EvaluationProfileValidationError,
    load_evaluation_profile_spec,
)
from optimizer.evaluation.profile_runner import EvaluationProfileRunner
from optimizer.evaluation.native_compatibility import NativeCompatibilityPreflightError
from optimizer.evaluation.profile_schema import EvaluationExecutionTarget


class EvaluationProfileCli:
    """CLI-компонент запуска evaluation profile."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов profile-run."""

        parser = argparse.ArgumentParser(description="Run task evaluation profile v0")
        parser.add_argument("--profile-file", required=True, help="Путь до YAML-конфига evaluation profile.")
        parser.add_argument(
            "--target",
            choices=["dsl_runtime", "native_runtime"],
            default="",
            help="Execution target. Если не задан, используется default_target из profile.",
        )
        parser.add_argument("--details", action="store_true", help="Включить подробный oracle-отчет участников.")
        parser.add_argument("--pretty", action="store_true", help="Печатать JSON в pretty-формате.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает profile-run и возвращает код завершения CLI."""

        parser = EvaluationProfileCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        load_env_file(project_root / ".env")

        profile_file = Path(args.profile_file).resolve()
        try:
            spec = load_evaluation_profile_spec(profile_file)
            target: EvaluationExecutionTarget = args.target or spec.default_target
            runner = EvaluationProfileRunner()
            result = runner.run(
                profile=spec,
                profile_file_dir=profile_file.parent,
                execution_target=target,
                include_details=bool(args.details),
            )
        except NativeCompatibilityPreflightError as exc:
            error_payload = {
                "error_type": "native_compatibility_preflight_failed",
                "message": str(exc),
                "preflight": exc.report.to_payload(),
            }
            if args.pretty:
                print(json.dumps(error_payload, ensure_ascii=False, indent=2), file=sys.stderr)
            else:
                print(json.dumps(error_payload, ensure_ascii=False), file=sys.stderr)
            return 1
        except (
            EvaluationProfileLoadError,
            EvaluationProfileValidationError,
            ValueError,
            FileNotFoundError,
            json.JSONDecodeError,
        ) as exc:
            print(f"[PROFILE ERROR] {exc}", file=sys.stderr)
            return 1

        payload = result.to_payload()
        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))
        return 0


def main() -> None:
    """Точка входа `python -m optimizer.evaluation.run_profile`."""

    raise SystemExit(EvaluationProfileCli.run())


if __name__ == "__main__":
    main()
