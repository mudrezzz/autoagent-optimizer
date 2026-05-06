"""Unit-тесты расчета middle-метрик из oracle-отчета."""

from __future__ import annotations

import pytest

from optimizer.metrics.middle_metrics import compute_middle_metrics


@pytest.mark.unit
def test_compute_middle_metrics_from_runtime_oracle_report() -> None:
    """Проверяет агрегирование coverage/violations/nodes/latency/llm calls по кейсам."""

    oracle_report = {
        "cases_total": 2,
        "results": [
            {
                "case_id": "c1",
                "passed": True,
                "rule_results": [{"passed": True, "message": "ok"}],
                "output_payload": {
                    "text": "answer 1",
                    "llm_calls": 1,
                    "node_outputs": {"a": {}, "b": {}},
                    "trace_summary": {"completed": 2, "duration_ms": 120},
                },
            },
            {
                "case_id": "c2",
                "passed": False,
                "rule_results": [{"passed": False, "message": "violation"}],
                "output_payload": {
                    "text": "answer 2",
                    "llm_calls": 2,
                    "node_outputs": {"a": {}, "b": {}, "c": {}},
                    "trace_summary": {"completed": 3, "duration_ms": 200},
                },
            },
        ],
    }

    result = compute_middle_metrics(oracle_report)

    assert result.coverage == 1.0
    assert result.rule_violations_total == 1
    assert result.nodes_executed_total == 5
    assert result.avg_nodes_per_case == 2.5
    assert result.llm_calls_total == 3
    assert result.duration_ms_total == 320
    assert result.duration_ms_avg == 160.0
    assert result.p95_case_duration_ms == 200.0


@pytest.mark.unit
def test_compute_middle_metrics_returns_zeroes_for_empty_report() -> None:
    """Проверяет защиту от пустого или отсутствующего oracle-отчета."""

    result = compute_middle_metrics(None)

    assert result.coverage == 0.0
    assert result.rule_violations_total == 0
    assert result.nodes_executed_total == 0
    assert result.avg_nodes_per_case == 0.0
    assert result.llm_calls_total == 0
    assert result.duration_ms_total == 0
    assert result.duration_ms_avg == 0.0
    assert result.p95_case_duration_ms == 0.0

