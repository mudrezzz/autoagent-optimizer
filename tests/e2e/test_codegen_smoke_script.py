"""E2E-тест smoke-скрипта генерации кода агента."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


def _resolve_powershell() -> str | None:
    """Определяет доступный бинарник PowerShell для запуска smoke-скрипта."""

    return shutil.which("powershell") or shutil.which("pwsh")


@pytest.mark.e2e
def test_codegen_smoke_script_passes() -> None:
    """Проверяет сквозной smoke-путь генерации и запуска сгенерированного агента."""

    shell_bin = _resolve_powershell()
    if shell_bin is None:
        pytest.skip("PowerShell не найден в окружении тестов.")

    script_path = _project_root() / "scripts" / "smoke_generate_agent_code.ps1"
    proc = subprocess.run(
        [shell_bin, "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert "[SMOKE] generated agent code demo completed successfully." in proc.stdout

