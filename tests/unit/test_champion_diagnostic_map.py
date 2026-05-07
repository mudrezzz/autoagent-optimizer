"""Unit-тесты построения diagnostic_map для champion export bundle."""

from __future__ import annotations

import pytest

from optimizer.champion.diagnostic_map import DiagnosticMapBuildError, build_diagnostic_map_payload


def _sample_arena_payload() -> dict:
    """Возвращает минимальный валидный Arena payload для unit-тестов diagnostic map."""

    return {
        "winner_id": "style_direct_candidate",
        "ranking": [
            "style_direct_candidate",
            "style_pattern_cleaner_candidate",
        ],
        "participants": [
            {"participant_id": "style_direct_candidate"},
            {"participant_id": "style_pattern_cleaner_candidate"},
        ],
        "comparison": {
            "winner_vs_challenger_diff": [
                {
                    "metric": "duration_ms_avg",
                    "direction": "asc",
                    "winner_value": 100.0,
                    "challenger_value": 80.0,
                    "delta_winner_minus_challenger": 20.0,
                    "winner_advantage": False,
                    "interpretation": "Winner медленнее challenger по latency.",
                },
                {
                    "metric": "pass_rate",
                    "direction": "desc",
                    "winner_value": 1.0,
                    "challenger_value": 0.5,
                    "delta_winner_minus_challenger": 0.5,
                    "winner_advantage": True,
                    "interpretation": "Winner лучше по качеству.",
                },
            ]
        },
        "diagnostics": {
            "participants": [
                {
                    "participant_id": "style_direct_candidate",
                    "signals": {
                        "top_bottlenecks": [
                            {
                                "stage": "synthesize",
                                "bottleneck_score": 0.72,
                                "reason": "Стадия synthesize чаще всего связана с rule failures.",
                                "suggested_interventions": [
                                    "Уточнить prompt для synthesis.",
                                    "Добавить validator после synthesis.",
                                ],
                            },
                            {
                                "stage": "validate",
                                "bottleneck_score": 0.25,
                                "reason": "Часть провалов связана с validate.",
                                "suggested_interventions": [
                                    "Расширить правила validate.",
                                ],
                            },
                        ]
                    },
                }
            ]
        },
    }


@pytest.mark.unit
def test_build_diagnostic_map_payload_contains_prioritized_points() -> None:
    """Проверяет, что diagnostic_map содержит приоритизированные точки оптимизации."""

    payload = build_diagnostic_map_payload(_sample_arena_payload())
    assert payload["version"] == "diagnostic_map_v0"
    assert payload["winner_id"] == "style_direct_candidate"
    assert payload["summary"]["points_total"] >= 2

    points = payload["top_optimization_points"]
    assert points[0]["priority"] == 1
    assert points[0]["participant_id"] == "style_direct_candidate"
    assert points[0]["source"] in {"winner_diagnostics", "comparison_diff"}
    assert points[0]["bottleneck_score"] >= points[-1]["bottleneck_score"]


@pytest.mark.unit
def test_build_diagnostic_map_payload_includes_cross_metric_gap_points() -> None:
    """Проверяет, что gap по comparison diff попадает в diagnostic_map как отдельная точка."""

    payload = build_diagnostic_map_payload(_sample_arena_payload())
    cross_points = [point for point in payload["top_optimization_points"] if point["source"] == "comparison_diff"]
    assert len(cross_points) == 1
    assert cross_points[0]["stage"] == "metric::duration_ms_avg"
    assert "gap" in " ".join(cross_points[0]["suggested_interventions"]).lower()


@pytest.mark.unit
def test_build_diagnostic_map_payload_rejects_invalid_input() -> None:
    """Проверяет, что builder выбрасывает ошибку при невалидном Arena payload."""

    with pytest.raises(DiagnosticMapBuildError):
        build_diagnostic_map_payload({"winner_id": "x"})

