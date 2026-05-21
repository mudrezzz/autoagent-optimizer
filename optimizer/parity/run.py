"""CLI запуска DSL-vs-native parity harness."""

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
from optimizer.parity.runner import DslNativeParityRunner


class DslNativeParityCli:
    """CLI-компонент запуска parity-проверки для evaluation profile."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов parity-run."""

        parser = argparse.ArgumentParser(description="Run DSL-vs-native structural parity harness")
        parser.add_argument("--profile-file", required=True, help="Путь до YAML-конфига evaluation profile.")
        parser.add_argument(
            "--cases-limit",
            type=int,
            default=1,
            help="Сколько dataset-кейсов проверять на participant (0 -> использовать budget.cases_limit, fallback=1).",
        )
        parser.add_argument(
            "--participant-id",
            action="append",
            default=[],
            help="Опциональный фильтр participant_id (можно передать аргумент несколько раз).",
        )
        parser.add_argument("--out-file", default="", help="Опциональный путь для сохранения JSON parity-отчета.")
        parser.add_argument(
            "--fail-on-mismatch",
            action="store_true",
            help="Вернуть exit code=1, если parity не пройден хотя бы у одного participant.",
        )
        parser.add_argument("--pretty", action="store_true", help="Печатать JSON в pretty-формате.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает parity-run и возвращает код завершения CLI."""

        parser = DslNativeParityCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        load_env_file(project_root / ".env")

        profile_file = Path(args.profile_file).resolve()
        try:
            profile = load_evaluation_profile_spec(profile_file)
            report = DslNativeParityRunner().run(
                profile=profile,
                profile_file_dir=profile_file.parent,
                cases_limit=int(args.cases_limit),
                participant_ids=list(args.participant_id or []),
            )
        except (
            EvaluationProfileLoadError,
            EvaluationProfileValidationError,
            ValueError,
            FileNotFoundError,
            json.JSONDecodeError,
            RuntimeError,
        ) as exc:
            print(f"[PARITY ERROR] {exc}", file=sys.stderr)
            return 1

        payload = report.to_payload()
        if args.out_file:
            out_file = Path(args.out_file).resolve()
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None),
                encoding="utf-8",
            )

        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))

        if args.fail_on_mismatch and not report.passed:
            return 1
        return 0


def main() -> None:
    """Точка входа для `python -m optimizer.parity.run`."""

    raise SystemExit(DslNativeParityCli.run())


if __name__ == "__main__":
    main()

