"""Integration-тесты CLI-валидатора DSL."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь к корню текущего проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.integration
@pytest.mark.parametrize(
    "example_name",
    ["direct_llm.yaml", "ocr_first.yaml", "hitl_gate.yaml"],
)
def test_cli_validate_accepts_reference_examples(example_name: str) -> None:
    """Проверяет, что CLI принимает все эталонные DSL-примеры."""

    file_path = _project_root() / "examples" / "dsl" / example_name
    proc = subprocess.run(
        [sys.executable, "-m", "optimizer.dsl.validate", "--file", str(file_path), "--pretty"],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["schema_version"] == "0.1"
    assert payload["nodes"] >= 1


@pytest.mark.integration
def test_cli_validate_returns_error_for_missing_file() -> None:
    """Проверяет, что CLI возвращает код ошибки для отсутствующего файла."""

    missing_file = _project_root() / "examples" / "dsl" / "missing_file.yaml"
    proc = subprocess.run(
        [sys.executable, "-m", "optimizer.dsl.validate", "--file", str(missing_file)],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 1
    assert "[DSL INVALID]" in proc.stderr

