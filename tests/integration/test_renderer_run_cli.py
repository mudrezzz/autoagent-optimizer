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

