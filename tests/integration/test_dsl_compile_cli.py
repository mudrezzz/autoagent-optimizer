"""Integration-тесты CLI компиляции DSL -> Graph IR."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает путь к корню проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.integration
@pytest.mark.parametrize("example_name", ["direct_llm.yaml", "ocr_first.yaml", "hitl_gate.yaml"])
def test_dsl_compile_cli_success(example_name: str, tmp_path: Path) -> None:
    """Проверяет успешную компиляцию эталонного DSL-файла через CLI."""

    dsl_path = _project_root() / "examples" / "dsl" / example_name
    output_ir_path = tmp_path / f"{example_name}.ir.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.dsl.compile",
            "--dsl-file",
            str(dsl_path),
            "--output-ir-file",
            str(output_ir_path),
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    assert len(lines) >= 2
    summary_payload = json.loads("\n".join(lines[:-1]))
    output_payload = json.loads(lines[-1])
    assert summary_payload["status"] == "success"
    assert Path(output_payload["output_ir_file"]).exists()


@pytest.mark.integration
def test_dsl_compile_cli_fails_for_invalid_input(tmp_path: Path) -> None:
    """Проверяет ошибку CLI при невалидном DSL-файле."""

    bad_dsl_path = tmp_path / "bad.yaml"
    bad_dsl_path.write_text("schema_version: '0.1'\nproject: {}\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "optimizer.dsl.compile", "--dsl-file", str(bad_dsl_path), "--pretty"],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 1
    assert "[DSL COMPILE ERROR]" in proc.stderr

