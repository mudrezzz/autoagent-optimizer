"""Утилиты загрузки и валидации DSL-файлов."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from optimizer.dsl.schema import AutoAgentDslSpec


class DslLoadError(ValueError):
    """Ошибка чтения или первичного парсинга DSL-файла."""


class DslValidationError(ValueError):
    """Ошибка валидации DSL относительно typed-схемы."""


def load_yaml_payload(file_path: Path) -> dict[str, Any]:
    """Читает YAML-файл и возвращает словарь payload."""

    if not file_path.exists():
        raise DslLoadError(f"DSL-файл не найден: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    try:
        payload = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise DslLoadError(f"YAML parsing error в `{file_path}`: {exc}") from exc

    if not isinstance(payload, dict):
        raise DslLoadError(f"Ожидался YAML-объект на верхнем уровне: {file_path}")

    return payload


def load_dsl_spec(file_path: Path) -> AutoAgentDslSpec:
    """Загружает DSL-файл и валидирует его через `AutoAgentDslSpec`."""

    payload = load_yaml_payload(file_path)
    try:
        return AutoAgentDslSpec.model_validate(payload)
    except ValidationError as exc:
        raise DslValidationError(str(exc)) from exc

