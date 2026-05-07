"""Построение diagnostic_map артефакта для champion export bundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DiagnosticMapBuildError(ValueError):
    """Ошибка построения diagnostic_map при некорректном Arena payload."""


@dataclass(frozen=True)
class DiagnosticPoint:
    """Одна приоритизированная точка оптимизации в diagnostic map."""

    priority: int
    participant_id: str
    stage: str
    bottleneck_score: float
    reason: str
    suggested_interventions: list[str]
    source: str

    def to_payload(self) -> dict[str, Any]:
        """Преобразует объект точки оптимизации в JSON-совместимый словарь."""

        return {
            "priority": self.priority,
            "participant_id": self.participant_id,
            "stage": self.stage,
            "bottleneck_score": self.bottleneck_score,
            "reason": self.reason,
            "suggested_interventions": self.suggested_interventions,
            "source": self.source,
        }


def build_diagnostic_map_payload(arena_payload: dict[str, Any]) -> dict[str, Any]:
    """Строит diagnostic_map c приоритизированными точками оптимизации."""

    _validate_arena_payload(arena_payload)

    winner_id = str(arena_payload.get("winner_id", ""))
    ranking = [str(item) for item in arena_payload.get("ranking", []) if isinstance(item, str)]
    challenger_id = ranking[1] if len(ranking) > 1 else ""

    diagnostic_participants = arena_payload.get("diagnostics", {}).get("participants", [])
    winner_diagnostics = _find_participant_diagnostics(diagnostic_participants, winner_id)

    points: list[DiagnosticPoint] = []
    points.extend(_winner_bottleneck_points(winner_id=winner_id, winner_diagnostics=winner_diagnostics))
    points.extend(_cross_metric_gap_points(arena_payload=arena_payload, winner_id=winner_id))

    points.sort(key=lambda item: item.bottleneck_score, reverse=True)
    prioritized_points = [
        DiagnosticPoint(
            priority=index + 1,
            participant_id=item.participant_id,
            stage=item.stage,
            bottleneck_score=item.bottleneck_score,
            reason=item.reason,
            suggested_interventions=item.suggested_interventions,
            source=item.source,
        ).to_payload()
        for index, item in enumerate(points)
    ]

    return {
        "version": "diagnostic_map_v0",
        "winner_id": winner_id,
        "challenger_id": challenger_id,
        "ranking": ranking,
        "top_optimization_points": prioritized_points,
        "summary": {
            "points_total": len(prioritized_points),
            "winner_points_total": sum(1 for item in prioritized_points if item["participant_id"] == winner_id),
            "cross_metric_points_total": sum(1 for item in prioritized_points if item["source"] == "comparison_diff"),
        },
    }


def _validate_arena_payload(arena_payload: dict[str, Any]) -> None:
    """Проверяет обязательные поля Arena payload перед построением diagnostic map."""

    if "winner_id" not in arena_payload:
        raise DiagnosticMapBuildError("В Arena payload отсутствует обязательное поле `winner_id`.")
    if "ranking" not in arena_payload:
        raise DiagnosticMapBuildError("В Arena payload отсутствует обязательное поле `ranking`.")
    if "diagnostics" not in arena_payload:
        raise DiagnosticMapBuildError("В Arena payload отсутствует обязательное поле `diagnostics`.")
    ranking = arena_payload.get("ranking")
    if not isinstance(ranking, list) or not ranking:
        raise DiagnosticMapBuildError("В Arena payload `ranking` должен быть непустым списком.")


def _find_participant_diagnostics(diagnostic_participants: Any, participant_id: str) -> dict[str, Any]:
    """Возвращает diagnostics конкретного участника по `participant_id`."""

    if not isinstance(diagnostic_participants, list):
        return {}
    for item in diagnostic_participants:
        if not isinstance(item, dict):
            continue
        if str(item.get("participant_id", "")) == participant_id:
            signals = item.get("signals")
            if isinstance(signals, dict):
                return signals
    return {}


def _winner_bottleneck_points(*, winner_id: str, winner_diagnostics: dict[str, Any]) -> list[DiagnosticPoint]:
    """Строит список точек оптимизации winner на базе его top bottlenecks."""

    top_bottlenecks = winner_diagnostics.get("top_bottlenecks", [])
    if not isinstance(top_bottlenecks, list):
        top_bottlenecks = []

    points: list[DiagnosticPoint] = []
    for item in top_bottlenecks:
        if not isinstance(item, dict):
            continue
        stage = str(item.get("stage", "unknown"))
        score = float(item.get("bottleneck_score", 0.0))
        reason = str(item.get("reason", f"stage `{stage}` требует анализа."))
        interventions = item.get("suggested_interventions", [])
        if not isinstance(interventions, list):
            interventions = []
        points.append(
            DiagnosticPoint(
                priority=0,
                participant_id=winner_id,
                stage=stage,
                bottleneck_score=round(max(score, 0.0), 6),
                reason=reason,
                suggested_interventions=[str(hint) for hint in interventions if isinstance(hint, str)][:5],
                source="winner_diagnostics",
            )
        )
    if points:
        return points
    return _winner_stage_watch_points(winner_id=winner_id, winner_diagnostics=winner_diagnostics)


def _winner_stage_watch_points(*, winner_id: str, winner_diagnostics: dict[str, Any]) -> list[DiagnosticPoint]:
    """Строит fallback-точки наблюдения по stage_aggregates, если bottleneck-провалы не обнаружены."""

    stage_aggregates = winner_diagnostics.get("stage_aggregates", [])
    if not isinstance(stage_aggregates, list):
        return []

    points: list[DiagnosticPoint] = []
    for item in stage_aggregates[:3]:
        if not isinstance(item, dict):
            continue
        stage = str(item.get("stage", "unknown"))
        score = float(item.get("bottleneck_score", 0.0))
        points.append(
            DiagnosticPoint(
                priority=0,
                participant_id=winner_id,
                stage=stage,
                bottleneck_score=round(max(score, 0.0), 6),
                reason=f"Провалы на stage `{stage}` не доминируют; держим под наблюдением для следующего цикла.",
                suggested_interventions=_watch_interventions(stage),
                source="winner_stage_watch",
            )
        )
    return points


def _cross_metric_gap_points(*, arena_payload: dict[str, Any], winner_id: str) -> list[DiagnosticPoint]:
    """Строит cross-metric точки из comparison diff, где winner уступает challenger."""

    comparison = arena_payload.get("comparison", {})
    if not isinstance(comparison, dict):
        return []
    diff_items = comparison.get("winner_vs_challenger_diff", [])
    if not isinstance(diff_items, list):
        return []

    points: list[DiagnosticPoint] = []
    for item in diff_items:
        if not isinstance(item, dict):
            continue
        winner_advantage = item.get("winner_advantage")
        if winner_advantage is not False:
            continue

        metric_name = str(item.get("metric", "unknown_metric"))
        delta = item.get("delta_winner_minus_challenger", 0.0)
        try:
            score = abs(float(delta))
        except (TypeError, ValueError):
            score = 0.0
        direction = str(item.get("direction", "desc"))
        reason = str(item.get("interpretation", "winner уступает challenger по сравнительной метрике."))

        points.append(
            DiagnosticPoint(
                priority=0,
                participant_id=winner_id,
                stage=f"metric::{metric_name}",
                bottleneck_score=round(score, 6),
                reason=reason,
                suggested_interventions=[
                    f"Перепроверить scoring-вклад метрики `{metric_name}` (direction={direction}).",
                    f"Сфокусировать следующую итерацию на закрытии gap по `{metric_name}`.",
                ],
                source="comparison_diff",
            )
        )
    return points


def _watch_interventions(stage: str) -> list[str]:
    """Возвращает рекомендации наблюдения для стабильных stage без явных провалов."""

    return [
        f"Оставить stage `{stage}` в мониторинге и отслеживать drift на следующем наборе кейсов.",
        f"Добавить targeted-кейсы для stage `{stage}`, чтобы повысить диагностическую чувствительность.",
    ]
