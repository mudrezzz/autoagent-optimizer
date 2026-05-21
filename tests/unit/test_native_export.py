"""Unit-тесты standalone native exporter (`langgraph-dai`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from optimizer.champion.native_export import NativeLanggraphDaiExporter
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
def test_native_exporter_supports_tool_node_kind(tmp_path: Path) -> None:
    """Проверяет, что exporter принимает Graph IR с `tool`-узлами в v0."""

    graph_ir = load_graph_ir_spec(_project_root() / "examples" / "graph_ir" / "ocr_first.ir.json")
    exporter = NativeLanggraphDaiExporter()
    result = exporter.export(
        graph_ir=graph_ir,
        prompt_templates={"invoice_repair_v1": "repair: {query}"},
        output_dir=tmp_path / "native_agent",
    )
    assert result.run_file.exists()
    workflow_source = result.workflow_file.read_text(encoding="utf-8")
    assert "def _execute_tool" in workflow_source


@pytest.mark.unit
def test_native_exporter_supports_hitl_gate_node_kind(tmp_path: Path) -> None:
    """Проверяет, что exporter принимает Graph IR с `hitl_gate` (без `tool`) в v0."""

    dsl_file = _project_root() / "examples" / "dsl" / "style_hitl_reviewer.yaml"
    from optimizer.dsl.compiler import DslToGraphIRCompiler

    compile_result = DslToGraphIRCompiler().compile_file(dsl_file)
    assert compile_result.graph_ir is not None

    exporter = NativeLanggraphDaiExporter()
    result = exporter.export(
        graph_ir=compile_result.graph_ir,
        prompt_templates={
            "style_rewrite_with_patterns_v1": "Перепиши пост: {draft_post}",
            "style_finalize_v1": "Финализируй пост: {text}",
        },
        output_dir=tmp_path / "native_agent",
    )
    assert result.run_file.exists()
    workflow_source = result.workflow_file.read_text(encoding="utf-8")
    assert "def _execute_hitl_gate" in workflow_source
