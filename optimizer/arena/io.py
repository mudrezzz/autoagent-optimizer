"""Утилиты чтения и валидации YAML-конфига турнира Architecture Arena."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from optimizer.arena.tournament_schema import ArenaTournamentSpec


class ArenaLoadError(ValueError):
    """Ошибка чтения или парсинга YAML-конфигурации турнира."""


class ArenaValidationError(ValueError):
    """Ошибка валидации структуры конфигурации турнира."""


def load_arena_yaml_payload(file_path: Path) -> dict[str, Any]:
    """Читает YAML-файл турнира и возвращает словарь верхнего уровня."""

    if not file_path.exists():
        raise ArenaLoadError(f"Файл конфигурации Arena не найден: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    try:
        payload = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ArenaLoadError(f"YAML parsing error в `{file_path}`: {exc}") from exc

    if not isinstance(payload, dict):
        raise ArenaLoadError(f"Ожидался YAML-объект на верхнем уровне: {file_path}")

    return payload


def load_arena_tournament_spec(file_path: Path) -> ArenaTournamentSpec:
    """Загружает и валидирует конфигурацию турнира Arena v0."""

    payload = load_arena_yaml_payload(file_path)
    try:
        return ArenaTournamentSpec.model_validate(payload)
    except ValidationError as exc:
        raise ArenaValidationError(str(exc)) from exc

