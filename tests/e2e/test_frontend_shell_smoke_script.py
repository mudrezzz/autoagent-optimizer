"""E2E-тест smoke-скрипта frontend capability shell."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь к корню проекта."""

    return Path(__file__).resolve().parents[2]


def _resolve_powershell() -> str | None:
    """Определяет доступный бинарник PowerShell для запуска smoke-скрипта."""

    return shutil.which("powershell") or shutil.which("pwsh")


@pytest.mark.e2e
def test_frontend_shell_smoke_script_passes() -> None:
    """Проверяет успешный e2e запуск smoke-сценария frontend shell."""

    shell_bin = _resolve_powershell()
    if shell_bin is None:
        pytest.skip("PowerShell не найден в окружении тестов.")

    script_path = _project_root() / "scripts" / "smoke_frontend_shell.ps1"
    proc = subprocess.run(
        [shell_bin, "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert "[SMOKE] frontend capability shell completed successfully." in proc.stdout

