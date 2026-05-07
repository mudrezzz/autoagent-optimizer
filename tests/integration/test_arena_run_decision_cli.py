"""Integration-тесты decision-budget конфигурации турнира Architecture Arena."""

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
def test_arena_run_cli_support_tournament_decision_budget() -> None:
    """Проверяет, что decision-конфиг использует 8 кейсов и hash_stable селектор."""

    arena_file = _project_root() / "examples" / "arena" / "support_tournament_ci_decision_v0.yaml"
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
    assert payload["budget_selector"] == "hash_stable"
    assert payload["cases_budget"] == 8
    assert payload["dataset_records_total"] >= 12
    assert payload["evaluated_records_total"] == 8
    assert len(payload["participants"]) == 3

