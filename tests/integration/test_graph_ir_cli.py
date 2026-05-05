"""Integration-тесты CLI-валидации Graph IR."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from optimizer.graph_ir.models import GraphIRSpec


def _project_root() -> Path:
    """Возвращает путь к корню проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.integration
@pytest.mark.parametrize(
    "example_name",
    ["direct_llm.ir.json", "ocr_first.ir.json", "hitl_gate.ir.json"],
)
def test_graph_ir_cli_accepts_reference_examples(example_name: str) -> None:
    """Проверяет успешную валидацию эталонных Graph IR примеров через CLI."""

    file_path = _project_root() / "examples" / "graph_ir" / example_name
    proc = subprocess.run(
        [sys.executable, "-m", "optimizer.graph_ir.validate", "--file", str(file_path), "--pretty"],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ir_version"] == "0.1"
    assert payload["nodes"] >= 2


@pytest.mark.integration
def test_graph_ir_roundtrip_for_reference_example() -> None:
    """Проверяет roundtrip сериализации/десериализации на референсном примере."""

    file_path = _project_root() / "examples" / "graph_ir" / "ocr_first.ir.json"
    source_payload = json.loads(file_path.read_text(encoding="utf-8"))
    spec = GraphIRSpec.model_validate(source_payload)
    restored = GraphIRSpec.model_validate_json(spec.model_dump_json())
    assert restored.model_dump(mode="json") == spec.model_dump(mode="json")

