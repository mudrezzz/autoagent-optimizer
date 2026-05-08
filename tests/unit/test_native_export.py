"""Unit-тесты standalone native exporter (`langgraph-dai`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from optimizer.champion.native_export import NativeExportBuildError, NativeLanggraphDaiExporter
from optimizer.graph_ir.io import load_graph_ir_spec


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_native_exporter_creates_standalone_package(tmp_path: Path) -> None:
    """Проверяет, что exporter создает standalone native package структуру."""

    graph_ir = load_graph_ir_spec(_project_root() / "examples" / "graph_ir" / "direct_llm.ir.json")
    exporter = NativeLanggraphDaiExporter()
    result = exporter.export(
        graph_ir=graph_ir,
        prompt_templates={"support_answer_v1": "Ответь на запрос: {query}"},
        output_dir=tmp_path / "native_agent",
        force=False,
    )

    assert result.run_file.exists()
    assert result.workflow_file.exists()
    assert result.prompts_file.exists()
    assert result.graph_ir_file.exists()
    assert result.requirements_file.exists()
    assert result.readme_file.exists()

    workflow_source = result.workflow_file.read_text(encoding="utf-8")
    assert "optimizer." not in workflow_source
    prompts_payload = json.loads(result.prompts_file.read_text(encoding="utf-8"))
    assert prompts_payload["support_answer_v1"] == "Ответь на запрос: {query}"


@pytest.mark.unit
def test_native_exporter_rejects_unsupported_node_kinds(tmp_path: Path) -> None:
    """Проверяет fail-fast на неподдержанных node kinds (`tool`/`hitl_gate`) в v0."""

    graph_ir = load_graph_ir_spec(_project_root() / "examples" / "graph_ir" / "hitl_gate.ir.json")
    exporter = NativeLanggraphDaiExporter()
    with pytest.raises(NativeExportBuildError):
        exporter.export(
            graph_ir=graph_ir,
            prompt_templates={"action_routing_v1": "route: {query}"},
            output_dir=tmp_path / "native_agent",
        )

