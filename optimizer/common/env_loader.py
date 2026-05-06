"""Минимальная загрузка env-переменных из `.env` файла."""

from __future__ import annotations

import os
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
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value

