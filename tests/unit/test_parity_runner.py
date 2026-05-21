"""Unit-тесты структурного DSL-vs-native parity comparator."""

from __future__ import annotations

import pytest

from optimizer.parity.runner import compare_structural_state


@pytest.mark.unit
def test_compare_structural_state_passes_on_equal_structure() -> None:
    """Проверяет, что comparator дает passed=true при эквивалентной структуре state."""

    dsl_state = {
        "executed_nodes": ["a", "b"],
        "skipped_nodes": ["c"],
        "errors": [],
        "node_outputs": {
            "a": {"text": "hello", "status": "ok"},
            "b": {"valid": True},
        },
        "trace": [
            {"node_id": "a", "status": "completed", "next_nodes": ["b"]},
            {"node_id": "b", "status": "completed", "next_nodes": []},
        ],
    }
    native_state = {
        "executed_nodes": ["a", "b"],
        "skipped_nodes": ["c"],
        "errors": [],
        "node_outputs": {
            "a": {"status": "ok", "text": "different-content-is-allowed"},
            "b": {"valid": False},
        },
        "trace": [
            {"node_id": "a", "status": "completed", "next_nodes": ["b"]},
            {"node_id": "b", "status": "completed", "next_nodes": []},
        ],
    }

    result = compare_structural_state(case_id="case-1", dsl_state=dsl_state, native_state=native_state)
    assert result.passed is True
    assert all(result.checks.values())
    assert result.mismatches == []


@pytest.mark.unit
def test_compare_structural_state_detects_mismatch() -> None:
    """Проверяет, что comparator возвращает mismatch по различающимся структурным полям."""

    dsl_state = {
        "executed_nodes": ["a", "b"],
        "skipped_nodes": [],
        "errors": [],
        "node_outputs": {"a": {"text": "hello"}},
        "trace": [{"node_id": "a", "status": "completed", "next_nodes": ["b"]}],
    }
    native_state = {
        "executed_nodes": ["a"],
        "skipped_nodes": ["b"],
        "errors": ["b: failed"],
        "node_outputs": {"a": {"text": "hello"}, "b": {"status": "fallback"}},
        "trace": [{"node_id": "a", "status": "completed", "next_nodes": []}],
    }

    result = compare_structural_state(case_id="case-2", dsl_state=dsl_state, native_state=native_state)
    assert result.passed is False
    assert any(check is False for check in result.checks.values())
    assert result.mismatches
    mismatch_names = {item["check"] for item in result.mismatches}
    assert "executed_nodes_equal" in mismatch_names
    assert "skipped_nodes_equal" in mismatch_names
    assert "errors_equal" in mismatch_names
