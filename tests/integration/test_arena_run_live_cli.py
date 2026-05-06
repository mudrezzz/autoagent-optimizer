"""Integration-тест live runtime-турнира Arena (опциональный, неблокирующий по умолчанию)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.live
def test_arena_run_cli_support_tournament_runtime_invariants() -> None:
    """Проверяет инварианты live runtime-прогона без фиксации winner."""

    if os.getenv("RUN_LIVE_ARENA", "0") != "1":
        pytest.skip("Live Arena тест отключен; установите RUN_LIVE_ARENA=1 для запуска.")

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
    assert payload["execution_mode"] == "runtime"
    assert payload["scoring_enabled"] is True
    assert payload["ranking_policy"][0] == {"name": "composite_score", "direction": "desc"}
    assert len(payload["participants"]) == 3
    assert len(payload["ranking"]) == 3
    assert sorted(payload["ranking"]) == sorted([item["participant_id"] for item in payload["participants"]])
    assert payload["winner_id"] in payload["ranking"]
    for participant in payload["participants"]:
        assert "middle_metrics" in participant
        assert "composite_score" in participant
        assert participant["middle_metrics"]["llm_calls_total"] >= 0

