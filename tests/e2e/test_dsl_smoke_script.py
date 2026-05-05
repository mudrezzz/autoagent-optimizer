"""E2E-тесты smoke-скрипта полной проверки DSL."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь к корню проекта для запуска e2e-команд."""

    return Path(__file__).resolve().parents[2]


def _resolve_powershell() -> str | None:
    """Определяет доступный бинарник PowerShell для запуска smoke-скрипта."""

    return shutil.which("powershell") or shutil.which("pwsh")


@pytest.mark.e2e
def test_smoke_script_validates_all_examples() -> None:
    """Проверяет, что smoke-скрипт успешно валидирует все DSL-примеры."""

    shell_bin = _resolve_powershell()
    if shell_bin is None:
        pytest.skip("PowerShell не найден в окружении тестов.")

    script_path = _project_root() / "scripts" / "smoke_validate_dsl.ps1"
    proc = subprocess.run(
        [shell_bin, "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert "[SMOKE] DSL validation completed successfully." in proc.stdout

