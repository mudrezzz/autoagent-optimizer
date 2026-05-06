"""Загрузчик и валидатор golden dataset в формате JSONL."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from optimizer.evaluation.dataset_schema import GoldenDatasetRecord, GoldenDatasetSummary


@dataclass(frozen=True)
class GoldenDatasetIssue:
    """Описание ошибки в конкретной строке JSONL датасета."""

    line_number: int
    message: str


class GoldenDatasetLoadError(ValueError):
    """Ошибки чтения/валидации golden dataset."""


@dataclass
class GoldenDatasetLoadResult:
    """Результат загрузки датасета: записи, сводка и список ошибок."""

    dataset_file: Path
    records: list[GoldenDatasetRecord]
    issues: list[GoldenDatasetIssue]

    @property
    def is_success(self) -> bool:
        """Возвращает `True`, если датасет загружен без ошибок."""

        return len(self.issues) == 0

    def summary(self) -> GoldenDatasetSummary:
        """Формирует типизированную сводку по загруженным валидным записям."""

        tags: set[str] = set()
        for record in self.records:
            tags.update(record.tags)
        case_ids = {record.case_id for record in self.records}
        return GoldenDatasetSummary(
            dataset_file=str(self.dataset_file),
            records_total=len(self.records),
            unique_case_ids=len(case_ids),
            tags_total=len(tags),
        )


class GoldenDatasetLoader:
    """Загрузчик JSONL golden dataset с построчной валидацией контракта."""

    def load_file(self, dataset_file: Path) -> GoldenDatasetLoadResult:
        """Читает JSONL файл и возвращает валидированные записи/ошибки."""

        resolved_file = dataset_file.resolve()
        if not resolved_file.exists():
            raise GoldenDatasetLoadError(f"Dataset файл не найден: {resolved_file}")

        records: list[GoldenDatasetRecord] = []
        issues: list[GoldenDatasetIssue] = []
        seen_case_ids: set[str] = set()

        with resolved_file.open("r", encoding="utf-8-sig") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                stripped = raw_line.strip()
                if not stripped:
                    # Пустые строки допустимы: игнорируем их для удобства редактирования.
                    continue

                payload = self._parse_json_line(stripped, line_number, issues)
                if payload is None:
                    continue

                record = self._validate_record(payload, line_number, issues)
                if record is None:
                    continue

                if record.case_id in seen_case_ids:
                    issues.append(
                        GoldenDatasetIssue(
                            line_number=line_number,
                            message=f"Дубликат case_id `{record.case_id}`.",
                        )
                    )
                    continue

                seen_case_ids.add(record.case_id)
                records.append(record)

        return GoldenDatasetLoadResult(dataset_file=resolved_file, records=records, issues=issues)

    def _parse_json_line(
        self,
        stripped_line: str,
        line_number: int,
        issues: list[GoldenDatasetIssue],
    ) -> dict[str, Any] | None:
        """Парсит одну строку JSONL и собирает ошибку, если JSON некорректен."""

        try:
            payload = json.loads(stripped_line)
        except json.JSONDecodeError as exc:
            issues.append(GoldenDatasetIssue(line_number=line_number, message=f"JSON parsing error: {exc.msg}"))
            return None

        if not isinstance(payload, dict):
            issues.append(
                GoldenDatasetIssue(
                    line_number=line_number,
                    message="Ожидался JSON-объект верхнего уровня.",
                )
            )
            return None

        return payload

    def _validate_record(
        self,
        payload: dict[str, Any],
        line_number: int,
        issues: list[GoldenDatasetIssue],
    ) -> GoldenDatasetRecord | None:
        """Валидирует payload строки через typed-схему записи."""

        try:
            return GoldenDatasetRecord.model_validate(payload)
        except ValidationError as exc:
            issues.append(
                GoldenDatasetIssue(
                    line_number=line_number,
                    message=str(exc),
                )
            )
            return None

