"""Integration-тесты CLI генерации кода агента."""

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
def test_agent_codegen_cli_from_dsl_and_generated_runner(tmp_path: Path) -> None:
    """Проверяет генерацию из DSL и запуск сгенерированного CLI-агента."""

    dsl_file = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    output_dir = tmp_path / "generated_direct_llm"

    codegen_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.codegen.generate",
            "--dsl-file",
            str(dsl_file),
            "--output-dir",
            str(output_dir),
            "--package-name",
            "direct_llm_demo_agent",
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert codegen_proc.returncode == 0, codegen_proc.stderr

    summary = json.loads(codegen_proc.stdout)
    runner_path = Path(summary["entrypoint_file"])
    assert runner_path.exists()

    payload_file = output_dir / "payload.json"
    payload_file.write_text('{"query":"What is this project for?"}', encoding="utf-8")

    run_proc = subprocess.run(
        [
            sys.executable,
            str(runner_path),
            "--payload-file",
            str(payload_file),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert run_proc.returncode == 0, run_proc.stderr
    run_payload = json.loads(run_proc.stdout)
    assert "executed_nodes" in run_payload
    assert "trace" in run_payload

