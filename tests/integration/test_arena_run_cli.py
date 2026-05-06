"""Integration-тесты CLI запуска турнира Architecture Arena."""

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
def test_arena_run_cli_support_tournament_success() -> None:
    """Проверяет успешный запуск arena CLI на эталонном турнире из examples."""

    arena_file = _project_root() / "examples" / "arena" / "support_tournament_v0.yaml"
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
    assert payload["winner_id"] == "direct_llm_candidate"
    assert payload["ranking"] == ["direct_llm_candidate", "ocr_first_candidate", "hitl_gate_candidate"]
    assert payload["cases_budget"] == 3
    assert payload["budget_policy"] == "equal_cases"
    assert payload["budget_unit"] == "cases"
    assert payload["budget_selector"] == "head"
    assert payload["scoring_enabled"] is True
    assert payload["scoring_normalization"] == "minmax"
    assert payload["ranking_policy"][0] == {"name": "composite_score", "direction": "desc"}
    assert len(payload["participants"]) == 3
    assert "composite_score" in payload["participants"][0]
    assert "middle_metrics" in payload["participants"][0]


@pytest.mark.integration
def test_arena_run_cli_fails_for_invalid_config(tmp_path: Path) -> None:
    """Проверяет ошибку CLI при невалидной конфигурации турнира (менее 2 участников)."""

    bad_arena = tmp_path / "bad_arena.yaml"
    bad_arena.write_text(
        "\n".join(
            [
                "version: arena_v0",
                "dataset_file: ../examples/datasets/golden_support_v1.jsonl",
                "execution_mode: expected_stub",
                "participants:",
                "  - participant_id: single",
                "    dsl_file: ../examples/dsl/direct_llm.yaml",
            ]
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.arena.run_tournament",
            "--arena-file",
            str(bad_arena),
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 1
    assert "[ARENA ERROR]" in proc.stderr
