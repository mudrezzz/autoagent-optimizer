"""Unit-тесты расчета диагностических сигналов по стадиям пайплайна."""

from __future__ import annotations

import pytest

from optimizer.metrics.diagnostic_signals import compute_diagnostic_signals


@pytest.mark.unit
def test_compute_diagnostic_signals_builds_stage_aggregates() -> None:
    """Проверяет расчет stage-агрегатов и bottleneck score на кейсах oracle-отчета."""

    oracle_report = {
        "cases_total": 2,
        "results": [
            {
                "case_id": "c1",
                "passed": False,
                "rule_results": [{"passed": False, "message": "missing"}],
                "output_payload": {
                    "executed_nodes": ["retrieve_docs", "generate_answer", "validate_output"],
                    "trace_summary": {"duration_ms": 1000},
                },
            },
            {
                "case_id": "c2",
                "passed": True,
                "rule_results": [{"passed": True, "message": "ok"}],
                "output_payload": {
                    "executed_nodes": ["retrieve_docs", "generate_answer", "validate_output"],
                    "trace_summary": {"duration_ms": 500},
                },
            },
        ],
    }
    node_stage_map = {
        "retrieve_docs": "retrieve",
        "generate_answer": "synthesize",
        "validate_output": "validate",
    }

    signals = compute_diagnostic_signals(oracle_report, node_stage_map=node_stage_map)

    assert signals["summary"]["cases_total"] == 2
    assert signals["summary"]["failed_cases_total"] == 1
    assert signals["summary"]["rule_failures_total"] == 1
    assert len(signals["stage_aggregates"]) == 3
    top_stage = signals["stage_aggregates"][0]
    assert top_stage["bottleneck_score"] >= 0.0
    assert top_stage["executions_total"] >= 1
    assert "top_bottlenecks" in signals
    assert "intervention_hints" in signals
    if signals["top_bottlenecks"]:
        top_bottleneck = signals["top_bottlenecks"][0]
        assert "reason" in top_bottleneck
        assert "suggested_interventions" in top_bottleneck


@pytest.mark.unit
def test_compute_diagnostic_signals_returns_empty_payload_for_missing_report() -> None:
    """Проверяет fallback-поведение при отсутствии oracle-данных."""

    signals = compute_diagnostic_signals(None)

    assert signals["summary"]["cases_total"] == 0
    assert signals["summary"]["failed_cases_total"] == 0
    assert signals["summary"]["failure_rate"] == 0.0
    assert signals["stage_aggregates"] == []
    assert signals["top_bottlenecks"] == []
    assert signals["intervention_hints"] == []
