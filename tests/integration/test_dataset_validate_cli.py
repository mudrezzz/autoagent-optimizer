"""Integration-тесты CLI валидации golden dataset."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_dataset_validate_cli_success() -> None:
    """Проверяет успешный запуск CLI на валидном эталонном датасете."""

    dataset_file = _project_root() / "examples" / "datasets" / "golden_support_v1.jsonl"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evaluation.validate_dataset",
            "--dataset-file",
            str(dataset_file),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "success"
    assert payload["records_total"] == 3
    assert payload["issues_total"] == 0


@pytest.mark.integration
def test_dataset_validate_cli_failure(tmp_path: Path) -> None:
    """Проверяет возврат ошибки CLI на невалидном JSONL."""

    dataset_file = tmp_path / "bad.jsonl"
    dataset_file.write_text('{"case_id":"x","input":{},"expected":{}}\n{"bad"', encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evaluation.validate_dataset",
            "--dataset-file",
            str(dataset_file),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 1
    assert "[DATASET ERROR]" in proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "failure"
    assert payload["issues_total"] >= 1

