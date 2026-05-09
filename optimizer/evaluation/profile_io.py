"""Утилиты чтения и валидации Evaluation Profile v0."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from optimizer.evaluation.profile_schema import EvaluationProfileSpec


class EvaluationProfileLoadError(ValueError):
    """Ошибка чтения/парсинга YAML-файла evaluation profile."""


class EvaluationProfileValidationError(ValueError):
    """Ошибка валидации структуры evaluation profile."""


def load_evaluation_profile_payload(file_path: Path) -> dict[str, Any]:
    """Читает YAML-файл profile и возвращает словарь верхнего уровня."""

    if not file_path.exists():
        raise EvaluationProfileLoadError(f"Файл evaluation profile не найден: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    try:
        payload = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise EvaluationProfileLoadError(f"YAML parsing error в `{file_path}`: {exc}") from exc

    if not isinstance(payload, dict):
        raise EvaluationProfileLoadError(f"Ожидался YAML-объект на верхнем уровне: {file_path}")
    return payload


def load_evaluation_profile_spec(file_path: Path) -> EvaluationProfileSpec:
    """Загружает и валидирует evaluation profile v0."""

    payload = load_evaluation_profile_payload(file_path)
    try:
        return EvaluationProfileSpec.model_validate(payload)
    except ValidationError as exc:
        raise EvaluationProfileValidationError(str(exc)) from exc
