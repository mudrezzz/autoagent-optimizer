"""Integration-тесты CLI executable oracle runner."""

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
def test_oracle_run_cli_expected_stub_success() -> None:
    """Проверяет успешный deterministic oracle-прогон через expected_stub."""

    dsl_file = _project_root() / "examples" / "dsl" / "style_direct_llm.yaml"
    dataset_file = _project_root() / "examples" / "datasets" / "golden_linkedin_stylizer_v1.jsonl"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evaluation.run_oracle",
            "--dsl-file",
            str(dsl_file),
            "--dataset-file",
            str(dataset_file),
            "--execution-mode",
            "expected_stub",
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["cases_total"] == 4
    assert payload["failed"] == 0
    assert payload["execution_mode"] == "expected_stub"


@pytest.mark.integration
def test_oracle_run_cli_fails_for_invalid_dataset(tmp_path: Path) -> None:
    """Проверяет ошибку CLI при невалидном golden dataset."""

    bad_dataset = tmp_path / "bad_dataset.jsonl"
    bad_dataset.write_text('{"case_id":"","input":{},"expected":{}}', encoding="utf-8")
    dsl_file = _project_root() / "examples" / "dsl" / "style_direct_llm.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evaluation.run_oracle",
            "--dsl-file",
            str(dsl_file),
            "--dataset-file",
            str(bad_dataset),
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 1
    assert "[ORACLE DATASET ERROR]" in proc.stderr
