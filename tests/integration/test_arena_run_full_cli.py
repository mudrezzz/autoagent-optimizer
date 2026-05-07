"""Integration-тесты full-budget конфигурации турнира Architecture Arena."""

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
def test_arena_run_cli_support_tournament_full_uses_all_dataset_records() -> None:
    """Проверяет, что full-конфиг использует весь dataset и не режет бюджет по кейсам."""

    arena_file = _project_root() / "examples" / "arena" / "support_tournament_ci_full_v0.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.arena.run_tournament",
            "--arena-file",
            str(arena_file),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr

    payload = json.loads(proc.stdout)
    assert payload["execution_mode"] == "expected_stub"
    assert payload["dataset_records_total"] >= 12
    assert payload["cases_budget"] == payload["dataset_records_total"]
    assert payload["evaluated_records_total"] == payload["dataset_records_total"]
    assert len(payload["participants"]) == 3
