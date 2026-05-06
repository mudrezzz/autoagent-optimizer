"""Integration-тесты CLI запуска runtime-рендерера."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает корневой путь проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_renderer_run_cli_with_dsl_file() -> None:
    """Проверяет запуск runtime CLI с источником DSL."""

    dsl_file = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.renderer.langgraph_dai.run",
            "--dsl-file",
            str(dsl_file),
            "--payload-json",
            '{"query":"Сформируй краткий ответ"}',
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert "executed_nodes" in payload
    assert "trace" in payload
    assert "node_events" in payload
    assert "trace_summary" in payload
    assert payload["trace_summary"]["events_total"] >= 1


@pytest.mark.integration
def test_renderer_run_cli_resume_path(tmp_path: Path) -> None:
    """Проверяет invoke->resume путь runtime CLI с checkpoint директорией."""

    dsl_file = _project_root() / "examples" / "dsl" / "hitl_gate.yaml"
    checkpoint_dir = tmp_path / "checkpoints"
    payload_start = tmp_path / "start.json"
    payload_resume = tmp_path / "resume.json"
    payload_start.write_text('{"query":"start","action_risk":"low"}', encoding="utf-8")
    payload_resume.write_text('{"action_risk":"high","review_decision":"approve"}', encoding="utf-8")

    start_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.renderer.langgraph_dai.run",
            "--dsl-file",
            str(dsl_file),
            "--payload-file",
            str(payload_start),
            "--task-id",
            "resume-cli-task",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert start_proc.returncode == 0, start_proc.stderr
    start_payload = json.loads(start_proc.stdout)
    assert start_payload["task_id"] == "resume-cli-task"

    resume_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.renderer.langgraph_dai.run",
            "--dsl-file",
            str(dsl_file),
            "--resume-task-id",
            "resume-cli-task",
            "--payload-file",
            str(payload_resume),
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert resume_proc.returncode == 0, resume_proc.stderr
    resume_payload = json.loads(resume_proc.stdout)
    assert resume_payload["task_id"] == "resume-cli-task"
    assert resume_payload["trace_summary"]["task_id"] == "resume-cli-task"


@pytest.mark.integration
def test_renderer_run_cli_resume_fails_for_unknown_task_id(tmp_path: Path) -> None:
    """Проверяет ошибку CLI при попытке resume без checkpoint по task_id."""

    dsl_file = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.renderer.langgraph_dai.run",
            "--dsl-file",
            str(dsl_file),
            "--resume-task-id",
            "unknown-task-id",
            "--checkpoint-dir",
            str(tmp_path / "checkpoints"),
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 1
    assert "[RUNTIME ERROR]" in proc.stderr
