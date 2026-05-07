"""Integration-тесты CLI генерации Evidence Pack v0."""

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
def test_evidence_pack_cli_builds_from_arena_file(tmp_path: Path) -> None:
    """Проверяет генерацию evidence pack по Arena YAML конфигу."""

    arena_file = _project_root() / "examples" / "arena" / "support_tournament_ci_v0.yaml"
    out_dir = tmp_path / "evidence_pack"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evidence.generate_pack",
            "--arena-file",
            str(arena_file),
            "--out-dir",
            str(out_dir),
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

    evidence_json = Path(payload["evidence_json_file"])
    evidence_md = Path(payload["evidence_markdown_file"])
    assert evidence_json.exists()
    assert evidence_md.exists()

    evidence_payload = json.loads(evidence_json.read_text(encoding="utf-8"))
    assert evidence_payload["comparison"]["winner_id"] == evidence_payload["tournament"]["winner_id"]
    assert "winner_vs_challenger_diff" in evidence_payload["comparison"]
    assert "participants" in evidence_payload["diagnostics"]


@pytest.mark.integration
def test_evidence_pack_cli_builds_from_saved_arena_result(tmp_path: Path) -> None:
    """Проверяет генерацию evidence pack по заранее сохраненному Arena JSON."""

    arena_file = _project_root() / "examples" / "arena" / "support_tournament_ci_v0.yaml"
    arena_result_file = tmp_path / "arena_result.json"

    arena_proc = subprocess.run(
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
    assert arena_proc.returncode == 0, arena_proc.stderr
    arena_result_file.write_text(arena_proc.stdout, encoding="utf-8")

    out_dir = tmp_path / "evidence_pack"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evidence.generate_pack",
            "--arena-result-file",
            str(arena_result_file),
            "--out-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "success"
    assert Path(payload["evidence_json_file"]).exists()
    assert Path(payload["evidence_markdown_file"]).exists()

