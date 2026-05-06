"""Unit-тесты компилятора DSL -> Graph IR."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.compile_report import CompileStatus
from optimizer.dsl.io import load_dsl_spec


def _project_root() -> Path:
    """Возвращает путь к корню проекта для чтения примеров."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.unit
@pytest.mark.parametrize("example_name", ["direct_llm.yaml", "ocr_first.yaml", "hitl_gate.yaml"])
def test_compiler_builds_graph_ir_for_reference_dsl(example_name: str) -> None:
    """Проверяет успешную компиляцию эталонных DSL-примеров в валидный Graph IR."""

    dsl_path = _project_root() / "examples" / "dsl" / example_name
    spec = load_dsl_spec(dsl_path)
    compiler = DslToGraphIRCompiler()
    result = compiler.compile_spec(spec, source=str(dsl_path))

    assert result.report.status == CompileStatus.SUCCESS
    assert result.graph_ir is not None
    assert len(result.report.node_mappings) == len(spec.graph.nodes)
    assert result.graph_ir.entry_node == spec.graph.entry_node


@pytest.mark.unit
def test_compiler_report_contains_node_mapping() -> None:
    """Проверяет, что отчет содержит детальные соответствия узлов DSL и IR."""

    dsl_path = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    spec = load_dsl_spec(dsl_path)
    compiler = DslToGraphIRCompiler()
    result = compiler.compile_spec(spec, source=str(dsl_path))
    assert result.graph_ir is not None
    mappings = result.report.node_mappings
    assert len(mappings) == 2
    assert mappings[0].dsl_node_id == "generate_answer"
    assert mappings[0].ir_node_id == "generate_answer"


@pytest.mark.unit
def test_compile_file_returns_failure_report_for_invalid_dsl(tmp_path: Path) -> None:
    """Проверяет, что при невалидном DSL возвращается failure-отчет и пустой IR."""

    invalid_dsl_path = tmp_path / "invalid.yaml"
    invalid_dsl_path.write_text("schema_version: '0.1'\nproject: {}\n", encoding="utf-8")
    compiler = DslToGraphIRCompiler()
    result = compiler.compile_file(invalid_dsl_path)
    assert result.graph_ir is None
    assert result.report.status == CompileStatus.FAILURE
    assert len(result.report.issues) >= 1

