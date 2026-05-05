"""Утилиты ввода/вывода Graph IR файлов."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from optimizer.graph_ir.models import GraphIRSpec
from optimizer.graph_ir.validators import GraphIRValidationError


class GraphIRLoadError(ValueError):
    """Ошибка чтения или JSON-парсинга Graph IR файла."""


class GraphIRSpecValidationError(ValueError):
    """Ошибка валидации Graph IR относительно typed-схемы."""


def load_graph_ir_payload(file_path: Path) -> dict[str, Any]:
    """Читает JSON-файл Graph IR и возвращает словарь payload."""

    if not file_path.exists():
        raise GraphIRLoadError(f"Graph IR файл не найден: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise GraphIRLoadError(f"JSON parsing error в `{file_path}`: {exc}") from exc

    if not isinstance(payload, dict):
        raise GraphIRLoadError(f"Ожидался JSON-объект на верхнем уровне: {file_path}")
    return payload


def load_graph_ir_spec(file_path: Path) -> GraphIRSpec:
    """Загружает Graph IR файл и валидирует его через `GraphIRSpec`."""

    payload = load_graph_ir_payload(file_path)
    try:
        return GraphIRSpec.model_validate(payload)
    except (ValidationError, GraphIRValidationError) as exc:
        raise GraphIRSpecValidationError(str(exc)) from exc

