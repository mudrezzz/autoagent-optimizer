"""CLI валидации golden dataset JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.evaluation.dataset_loader import GoldenDatasetLoader


class GoldenDatasetValidateCli:
    """CLI-компонент проверки golden dataset перед evaluation-прогонами."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер аргументов проверки датасета."""

        parser = argparse.ArgumentParser(description="Валидация golden dataset JSONL")
        parser.add_argument("--dataset-file", required=True, help="Путь до JSONL файла golden dataset.")
        parser.add_argument("--pretty", action="store_true", help="Печатать summary в pretty JSON.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Выполняет загрузку/валидацию и возвращает код завершения CLI."""

        parser = GoldenDatasetValidateCli.build_parser()
        args = parser.parse_args(argv)

        loader = GoldenDatasetLoader()
        result = loader.load_file(Path(args.dataset_file))

        summary_payload = result.summary().model_dump(mode="json")
        summary_payload["issues_total"] = len(result.issues)
        summary_payload["status"] = "success" if result.is_success else "failure"
        if args.pretty:
            print(json.dumps(summary_payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary_payload, ensure_ascii=False))

        if not result.is_success:
            for issue in result.issues:
                print(f"[DATASET ERROR] line={issue.line_number}: {issue.message}", file=sys.stderr)
            return 1

        return 0


def main() -> None:
    """Точка входа для `python -m optimizer.evaluation.validate_dataset`."""

    raise SystemExit(GoldenDatasetValidateCli.run())


if __name__ == "__main__":
    main()

