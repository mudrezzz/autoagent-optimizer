"""Unit-тесты сборки Evidence Pack v0 из Arena payload."""

from __future__ import annotations

import pytest

from optimizer.evidence.pack_builder import EvidencePackBuildError, build_evidence_pack_payload


def _sample_arena_payload() -> dict:
    """Возвращает минимальный валидный Arena payload для unit-тестов evidence builder."""

    return {
        "dataset_file": "examples/datasets/golden_linkedin_stylizer_v1.jsonl",
        "execution_mode": "expected_stub",
        "evaluator_mode": "rule_based_v0",
        "cases_budget": 4,
        "dataset_records_total": 12,
        "evaluated_records_total": 4,
        "winner_id": "p1",
        "ranking": ["p1", "p2", "p3"],
        "participants": [
            {
                "participant_id": "p1",
                "pass_rate": 1.0,
                "passed": 4,
                "failed": 0,
                "composite_score": 1.0,
                "middle_metrics": {
                    "coverage": 1.0,
                    "rule_violations_total": 0,
                    "llm_calls_total": 0,
                    "duration_ms_avg": 0.0,
                },
            },
            {
                "participant_id": "p2",
                "pass_rate": 0.75,
                "passed": 3,
                "failed": 1,
                "composite_score": 0.8,
                "middle_metrics": {
                    "coverage": 1.0,
                    "rule_violations_total": 5,
                    "llm_calls_total": 0,
                    "duration_ms_avg": 0.0,
                },
            },
            {
                "participant_id": "p3",
                "pass_rate": 0.0,
                "passed": 0,
                "failed": 4,
                "composite_score": 0.1,
                "middle_metrics": {
                    "coverage": 1.0,
                    "rule_violations_total": 15,
                    "llm_calls_total": 0,
                    "duration_ms_avg": 0.0,
                },
            },
        ],
        "scoring_policy": [
            {"name": "pass_rate", "direction": "desc", "weight": 0.6},
            {"name": "rule_violations_total", "direction": "asc", "weight": 0.3},
            {"name": "duration_ms_avg", "direction": "asc", "weight": 0.1},
        ],
        "comparison": {"winner_id": "p1", "ranking": ["p1", "p2", "p3"], "participants": []},
        "diagnostics": {
            "participants": [
                {
                    "participant_id": "p1",
                    "signals": {
                        "stage_aggregates": [{"stage": "synthesize", "rule_failures_total": 0, "touched_failed_cases": 0}],
                        "top_bottlenecks": [],
                        "intervention_hints": [],
                    },
                },
                {
                    "participant_id": "p2",
                    "signals": {
                        "stage_aggregates": [{"stage": "validate", "rule_failures_total": 5, "touched_failed_cases": 1}],
                        "top_bottlenecks": [{"stage": "validate", "bottleneck_score": 0.3}],
                        "intervention_hints": ["Ужесточить validator правила."],
                    },
                },
                {
                    "participant_id": "p3",
                    "signals": {
                        "stage_aggregates": [{"stage": "unknown", "rule_failures_total": 15, "touched_failed_cases": 4}],
                        "top_bottlenecks": [{"stage": "unknown", "bottleneck_score": 2.0}],
                        "intervention_hints": ["Переработать архитектуру кандидата."],
                    },
                },
            ]
        },
    }


@pytest.mark.unit
def test_build_evidence_pack_payload_contains_dual_sections() -> None:
    """Проверяет, что evidence pack содержит отдельные comparison и diagnostics секции."""

    payload = build_evidence_pack_payload(_sample_arena_payload())
    assert payload["version"] == "evidence_pack_v0"
    assert payload["comparison"]["winner_id"] == "p1"
    assert payload["tournament"]["challenger_id"] == "p2"
    assert len(payload["comparison"]["participants"]) == 3
    assert len(payload["diagnostics"]["participants"]) == 3
    assert "winner_vs_challenger_diff" in payload["comparison"]
    assert len(payload["comparison"]["winner_vs_challenger_diff"]) >= 3


@pytest.mark.unit
def test_build_evidence_pack_payload_exposes_challenger_recommendations() -> None:
    """Проверяет, что evidence pack формирует приоритетные рекомендации для challenger."""

    payload = build_evidence_pack_payload(_sample_arena_payload())
    actions = payload["recommendations"]["for_challenger_priority_actions"]
    assert len(actions) >= 2
    assert any("p2" in item for item in actions)


@pytest.mark.unit
def test_build_evidence_pack_payload_rejects_invalid_input() -> None:
    """Проверяет валидацию входного контракта Arena payload."""

    with pytest.raises(EvidencePackBuildError):
        build_evidence_pack_payload({"winner_id": "x", "ranking": ["x"]})

