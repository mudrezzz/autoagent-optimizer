"""Сборка Evidence Pack v0 из JSON-результата Arena турнира."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class EvidencePackBuildError(ValueError):
    """Ошибка сборки Evidence Pack при некорректном входном контракте Arena."""


@dataclass(frozen=True)
class EvidencePackFiles:
    """Пути к сформированным артефактам Evidence Pack."""

    json_file: str
    markdown_file: str


def build_evidence_pack_payload(arena_payload: dict[str, Any]) -> dict[str, Any]:
    """Строит нормализованный Evidence Pack payload с секциями comparison/diagnostics."""

    _validate_arena_payload(arena_payload)

    ranking = [str(item) for item in arena_payload.get("ranking", []) if isinstance(item, str)]
    winner_id = str(arena_payload.get("winner_id", ""))
    challenger_id = ranking[1] if len(ranking) > 1 else ""
    participants = arena_payload.get("participants", [])
    diagnostics = arena_payload.get("diagnostics", {}).get("participants", [])

    participant_by_id = {
        str(item.get("participant_id")): item
        for item in participants
        if isinstance(item, dict) and isinstance(item.get("participant_id"), str)
    }
    diagnostic_by_id = {
        str(item.get("participant_id")): item.get("signals", {})
        for item in diagnostics
        if isinstance(item, dict) and isinstance(item.get("participant_id"), str)
    }

    comparison_participants: list[dict[str, Any]] = []
    for participant_id in ranking:
        source = participant_by_id.get(participant_id, {})
        comparison_participants.append(
            {
                "participant_id": participant_id,
                "comparative_metrics": {
                    "pass_rate": source.get("pass_rate"),
                    "passed": source.get("passed"),
                    "failed": source.get("failed"),
                    "composite_score": source.get("composite_score"),
                    "middle_metrics": source.get("middle_metrics", {}),
                },
            }
        )

    diagnostics_participants: list[dict[str, Any]] = []
    for participant_id in ranking:
        signals = diagnostic_by_id.get(participant_id, {})
        diagnostics_participants.append(
            {
                "participant_id": participant_id,
                "diagnostic_signals_by_stage": signals.get("stage_aggregates", []),
                "top_bottlenecks": signals.get("top_bottlenecks", []),
                "intervention_hints": signals.get("intervention_hints", []),
            }
        )

    comparative_diff = _build_winner_challenger_diff(
        winner_id=winner_id,
        challenger_id=challenger_id,
        participant_by_id=participant_by_id,
        scoring_policy=arena_payload.get("scoring_policy", []),
    )

    return {
        "version": "evidence_pack_v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "tournament": {
            "dataset_file": arena_payload.get("dataset_file"),
            "execution_mode": arena_payload.get("execution_mode"),
            "evaluator_mode": arena_payload.get("evaluator_mode"),
            "cases_budget": arena_payload.get("cases_budget"),
            "dataset_records_total": arena_payload.get("dataset_records_total"),
            "evaluated_records_total": arena_payload.get("evaluated_records_total"),
            "winner_id": winner_id,
            "challenger_id": challenger_id,
            "ranking": ranking,
        },
        "comparison": {
            "winner_id": winner_id,
            "challenger_id": challenger_id,
            "participants": comparison_participants,
            "winner_vs_challenger_diff": comparative_diff,
        },
        "diagnostics": {
            "participants": diagnostics_participants,
        },
        "recommendations": _build_recommendations(
            winner_id=winner_id,
            challenger_id=challenger_id,
            diagnostics_participants=diagnostics_participants,
            comparative_diff=comparative_diff,
        ),
    }


def render_evidence_markdown(pack_payload: dict[str, Any]) -> str:
    """Рендерит человекочитаемый markdown-отчет из Evidence Pack payload."""

    tournament = pack_payload.get("tournament", {})
    comparison = pack_payload.get("comparison", {})
    diagnostics = pack_payload.get("diagnostics", {})
    recommendations = pack_payload.get("recommendations", {})

    lines: list[str] = []
    lines.append("# Evidence Pack v0")
    lines.append("")
    lines.append("## Tournament Summary")
    lines.append(f"- generated_at_utc: `{pack_payload.get('generated_at_utc', '')}`")
    lines.append(f"- dataset_file: `{tournament.get('dataset_file', '')}`")
    lines.append(f"- execution_mode: `{tournament.get('execution_mode', '')}`")
    lines.append(f"- winner: `{tournament.get('winner_id', '')}`")
    lines.append(f"- challenger: `{tournament.get('challenger_id', '')}`")
    lines.append(f"- cases_budget: `{tournament.get('cases_budget', 0)}`")
    lines.append("")
    lines.append("## Comparison")
    lines.append("")
    for item in comparison.get("participants", []):
        participant_id = item.get("participant_id", "")
        metrics = item.get("comparative_metrics", {})
        middle_metrics = metrics.get("middle_metrics", {})
        lines.append(f"### {participant_id}")
        lines.append(f"- pass_rate: `{metrics.get('pass_rate')}`")
        lines.append(f"- passed/failed: `{metrics.get('passed')}` / `{metrics.get('failed')}`")
        lines.append(f"- composite_score: `{metrics.get('composite_score')}`")
        lines.append(
            "- middle_metrics: "
            f"`rule_viol={middle_metrics.get('rule_violations_total')}`, "
            f"`llm_calls={middle_metrics.get('llm_calls_total')}`, "
            f"`avg_ms={middle_metrics.get('duration_ms_avg')}`"
        )
        lines.append("")

    lines.append("### Winner vs Challenger Diff")
    diff_items = comparison.get("winner_vs_challenger_diff", [])
    if not diff_items:
        lines.append("- нет данных для diff (недостаточно участников).")
    else:
        for diff in diff_items:
            lines.append(
                f"- `{diff.get('metric')}`: winner=`{diff.get('winner_value')}`, "
                f"challenger=`{diff.get('challenger_value')}`, "
                f"direction=`{diff.get('direction')}`, "
                f"winner_advantage=`{diff.get('winner_advantage')}`"
            )
            lines.append(f"  note: {diff.get('interpretation')}")
    lines.append("")

    lines.append("## Diagnostics")
    lines.append("")
    for item in diagnostics.get("participants", []):
        participant_id = item.get("participant_id", "")
        lines.append(f"### {participant_id}")
        stage_aggregates = item.get("diagnostic_signals_by_stage", [])
        if stage_aggregates:
            for stage in stage_aggregates:
                lines.append(
                    f"- stage `{stage.get('stage')}`: "
                    f"failures=`{stage.get('rule_failures_total')}`, "
                    f"failed_cases=`{stage.get('touched_failed_cases')}`, "
                    f"avg_ms=`{stage.get('avg_duration_ms')}`"
                )
        else:
            lines.append("- stage-агрегаты отсутствуют.")

        hints = item.get("intervention_hints", [])
        if hints:
            lines.append("- intervention_hints:")
            for hint in hints[:5]:
                lines.append(f"  - {hint}")
        else:
            lines.append("- intervention_hints: нет.")
        lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    for action in recommendations.get("for_challenger_priority_actions", []):
        lines.append(f"- {action}")
    if not recommendations.get("for_challenger_priority_actions"):
        lines.append("- Рекомендации отсутствуют.")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def _validate_arena_payload(arena_payload: dict[str, Any]) -> None:
    """Проверяет обязательные поля входного Arena payload перед сборкой пакета."""

    required_fields = ("winner_id", "ranking", "participants", "comparison", "diagnostics")
    for field_name in required_fields:
        if field_name not in arena_payload:
            raise EvidencePackBuildError(f"В Arena payload отсутствует обязательное поле `{field_name}`.")

    if not isinstance(arena_payload.get("ranking"), list) or len(arena_payload.get("ranking", [])) < 2:
        raise EvidencePackBuildError("В Arena payload `ranking` должен содержать минимум 2 участника.")


def _build_winner_challenger_diff(
    *,
    winner_id: str,
    challenger_id: str,
    participant_by_id: dict[str, dict[str, Any]],
    scoring_policy: Any,
) -> list[dict[str, Any]]:
    """Формирует explainable diff между winner и challenger по comparative метрикам."""

    if not winner_id or not challenger_id:
        return []

    winner = participant_by_id.get(winner_id, {})
    challenger = participant_by_id.get(challenger_id, {})
    if not winner or not challenger:
        return []

    metric_directions = _build_metric_directions(scoring_policy)
    metric_names = [
        "pass_rate",
        "passed",
        "failed",
        "composite_score",
        "coverage",
        "rule_violations_total",
        "llm_calls_total",
        "duration_ms_avg",
        "p95_case_duration_ms",
    ]

    diff_items: list[dict[str, Any]] = []
    for metric_name in metric_names:
        winner_value = _resolve_metric_value(winner, metric_name)
        challenger_value = _resolve_metric_value(challenger, metric_name)
        if winner_value is None or challenger_value is None:
            continue

        direction = metric_directions.get(metric_name, _default_direction(metric_name))
        delta = float(winner_value) - float(challenger_value)
        winner_advantage = bool(delta >= 0) if direction == "desc" else bool(delta <= 0)
        interpretation = _build_diff_interpretation(
            metric_name=metric_name,
            direction=direction,
            winner_advantage=winner_advantage,
            delta=delta,
        )
        diff_items.append(
            {
                "metric": metric_name,
                "direction": direction,
                "winner_value": winner_value,
                "challenger_value": challenger_value,
                "delta_winner_minus_challenger": round(delta, 6),
                "winner_advantage": winner_advantage,
                "interpretation": interpretation,
            }
        )

    return diff_items


def _build_metric_directions(scoring_policy: Any) -> dict[str, str]:
    """Собирает карту направлений метрик из scoring policy турнира."""

    directions: dict[str, str] = {}
    if not isinstance(scoring_policy, list):
        return directions
    for item in scoring_policy:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        direction = item.get("direction")
        if isinstance(name, str) and direction in ("asc", "desc"):
            directions[name] = direction
    return directions


def _resolve_metric_value(participant: dict[str, Any], metric_name: str) -> float | int | None:
    """Извлекает значение метрики участника из top-level и middle_metrics полей."""

    if metric_name in ("pass_rate", "passed", "failed", "composite_score"):
        value = participant.get(metric_name)
        return value if isinstance(value, (int, float)) else None
    middle_metrics = participant.get("middle_metrics", {})
    if isinstance(middle_metrics, dict):
        value = middle_metrics.get(metric_name)
        return value if isinstance(value, (int, float)) else None
    return None


def _default_direction(metric_name: str) -> str:
    """Возвращает direction по умолчанию для метрики, если policy его не задал."""

    if metric_name in ("failed", "rule_violations_total", "llm_calls_total", "duration_ms_avg", "p95_case_duration_ms"):
        return "asc"
    return "desc"


def _build_diff_interpretation(
    *,
    metric_name: str,
    direction: str,
    winner_advantage: bool,
    delta: float,
) -> str:
    """Строит короткое объяснение comparative diff между winner и challenger."""

    if direction == "desc":
        if winner_advantage:
            return f"Метрика `{metric_name}` оптимизируется на рост; winner выше challenger на {round(abs(delta), 6)}."
        return f"Метрика `{metric_name}` оптимизируется на рост; winner ниже challenger на {round(abs(delta), 6)}."

    if winner_advantage:
        return f"Метрика `{metric_name}` оптимизируется на снижение; winner ниже challenger на {round(abs(delta), 6)}."
    return f"Метрика `{metric_name}` оптимизируется на снижение; winner выше challenger на {round(abs(delta), 6)}."


def _build_recommendations(
    *,
    winner_id: str,
    challenger_id: str,
    diagnostics_participants: list[dict[str, Any]],
    comparative_diff: list[dict[str, Any]],
) -> dict[str, Any]:
    """Формирует приоритетные рекомендации для challenger на основе diff и diagnostics."""

    challenger_hints: list[str] = []
    for participant in diagnostics_participants:
        if participant.get("participant_id") != challenger_id:
            continue
        hints = participant.get("intervention_hints", [])
        if isinstance(hints, list):
            challenger_hints = [str(item) for item in hints if isinstance(item, str)]
        break

    metric_gaps = [
        diff["metric"]
        for diff in comparative_diff
        if isinstance(diff, dict) and diff.get("winner_advantage") is True
    ]
    metric_gap_text = ", ".join(metric_gaps[:5]) if metric_gaps else "существенных метрик"

    actions: list[str] = []
    if challenger_id:
        actions.append(
            f"Сфокусировать следующую итерацию `{challenger_id}` на метриках отставания: {metric_gap_text}."
        )
    if winner_id and challenger_id:
        actions.append(
            f"Сравнить prompt/graph-структуру `{winner_id}` и `{challenger_id}` в узлах с максимальным bottleneck_score."
        )
    for hint in challenger_hints[:4]:
        actions.append(hint)

    # Убираем дубли, сохраняя порядок.
    unique_actions: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        unique_actions.append(action)

    return {"for_challenger_priority_actions": unique_actions}

