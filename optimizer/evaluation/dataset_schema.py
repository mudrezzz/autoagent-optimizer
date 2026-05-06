"""Typed-схемы golden dataset для evaluation контура."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class GoldenDatasetRecord(BaseModel):
    """Одна запись golden dataset с входом, ожидаемым результатом и метаданными."""

    case_id: str = Field(..., min_length=1, description="Уникальный идентификатор кейса.")
    input: dict[str, Any] = Field(..., description="Входной payload для прогона workflow.")
    expected: dict[str, Any] = Field(..., description="Ожидаемый эталонный результат кейса.")
    tags: list[str] = Field(default_factory=list, description="Теги кейса для фильтрации/срезов.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Дополнительные технические метаданные.")

    @model_validator(mode="after")
    def validate_non_empty_payloads(self) -> "GoldenDatasetRecord":
        """Проверяет, что обязательные payload-блоки не пустые."""

        if not self.input:
            raise ValueError("Поле `input` не должно быть пустым объектом.")
        if not self.expected:
            raise ValueError("Поле `expected` не должно быть пустым объектом.")
        return self


class GoldenDatasetSummary(BaseModel):
    """Сводка по валидному golden dataset, используемая в CLI и smoke."""

    dataset_file: str = Field(..., min_length=1, description="Путь к исходному JSONL файлу.")
    records_total: int = Field(..., ge=0, description="Общее количество валидных записей.")
    unique_case_ids: int = Field(..., ge=0, description="Количество уникальных case_id.")
    tags_total: int = Field(..., ge=0, description="Количество уникальных тегов.")

