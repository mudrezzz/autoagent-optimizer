"""Минимальная загрузка env-переменных из `.env` файла."""

from __future__ import annotations

import os
import re
from pathlib import Path


def load_env_file(env_path: Path) -> None:
    """Загружает пары `KEY=VALUE` из файла в `os.environ`, не перезаписывая существующие."""

    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = _normalize_env_value(value)
        if key and key not in os.environ:
            os.environ[key] = value


def _normalize_env_value(raw_value: str) -> str:
    """Нормализует значение env-переменной и убирает inline-комментарии."""

    value = raw_value.strip()
    if not value:
        return value

    # Для quoted значений сохраняем `#` как часть значения.
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Для unquoted значений удаляем inline-комментарий вида ` ... # comment`.
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    return value
