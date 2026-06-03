"""Deterministic metric-crafting proposal generator for task-specific evaluation profiles."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


def build_metric_crafting_proposal(
    *,
    arena_id: str,
    candidate_set_draft: dict[str, Any] | None,
    evaluation_profile: dict[str, Any],
    candidate_features: dict[str, bool],
    created_at: str,
) -> dict[str, Any]:
    """Строит HITL proposal метрик без автоприменения к evaluation profile."""

    existing_refs = _build_existing_metric_refs(evaluation_profile=evaluation_profile)
    task_brief = _resolve_task_brief(candidate_set_draft=candidate_set_draft)
    proposal_items = [
        item
        for item in _build_style_metric_items(candidate_features=candidate_features)
        if (str(item.get("metric_kind", "")), str(item.get("metric_id", ""))) not in existing_refs
    ]
    if not proposal_items:
        proposal_items = _build_noop_review_items(evaluation_profile=evaluation_profile)
    return {
        "proposal_id": f"mp_{uuid4().hex[:10]}",
        "arena_id": arena_id,
        "profile_id": str(evaluation_profile.get("profile_id", "")),
        "status": "draft",
        "source": "deterministic_metric_crafter_v0",
        "created_at": created_at,
        "summary": _build_summary(task_brief=task_brief, proposal_items=proposal_items),
        "items": proposal_items,
    }


def _build_existing_metric_refs(*, evaluation_profile: dict[str, Any]) -> set[tuple[str, str]]:
    """Собирает уже существующие metric refs, чтобы proposal не дублировал профиль."""

    refs: set[tuple[str, str]] = set()
    for item in evaluation_profile.get("comparative_metrics", []):
        if isinstance(item, dict):
            metric_id = str(item.get("metric_id", "")).strip()
            if metric_id:
                refs.add(("comparative", metric_id))
    for item in evaluation_profile.get("diagnostic_signals", []):
        if isinstance(item, dict):
            signal_id = str(item.get("signal_id", "")).strip()
            if signal_id:
                refs.add(("diagnostic", signal_id))
    return refs


def _resolve_task_brief(*, candidate_set_draft: dict[str, Any] | None) -> str:
    """Достает brief из candidate draft, если он уже сформирован."""

    if not isinstance(candidate_set_draft, dict):
        return ""
    return str(candidate_set_draft.get("task_brief", "")).strip()


def _build_summary(*, task_brief: str, proposal_items: list[dict[str, Any]]) -> str:
    """Формирует краткое объяснение proposal для UI и chat summary."""

    if not proposal_items:
        return "No new task-specific metrics were proposed."
    if task_brief:
        return f"Prepared {len(proposal_items)} task-specific metric suggestion(s) from the battle brief."
    return f"Prepared {len(proposal_items)} task-specific metric suggestion(s) from selected candidates and profile context."


def _build_style_metric_items(*, candidate_features: dict[str, bool]) -> list[dict[str, Any]]:
    """Возвращает v0-набор метрик для демо stylizer и близких style-rewrite задач."""

    has_llm = bool(candidate_features.get("llm", False))
    has_tool = bool(candidate_features.get("tool", False))
    has_hitl = bool(candidate_features.get("hitl", False))
    return [
        _comparative_item(
            metric_id="human_likeness",
            title="Human-likeness score",
            description="Ranks whether the rewritten post sounds like a human author rather than generic AI output.",
            weight=0.3,
            rationale="The battle goal is style transformation, so semantic quality alone is not enough.",
            recommended_evaluators=["llm_judge"],
            required_features=["llm"] if has_llm else [],
        ),
        _comparative_item(
            metric_id="narrative_preservation",
            title="Narrative preservation",
            description="Checks that the original thread, point and proof structure survive the rewrite.",
            weight=0.25,
            rationale="A candidate can remove AI patterns while damaging the post meaning; this metric catches that tradeoff.",
            recommended_evaluators=["llm_judge", "golden_oracle"],
            required_features=[],
        ),
        _comparative_item(
            metric_id="ai_pattern_reduction",
            title="AI-pattern reduction",
            description="Scores removal of known AI cliches, over-structured phrasing and synthetic enthusiasm.",
            weight=0.25,
            rationale="This is the core business objective for the stylizer demo.",
            recommended_evaluators=["llm_judge", "executable_validator"],
            required_features=["tool"] if has_tool else [],
        ),
        _comparative_item(
            metric_id="length_discipline",
            title="Length discipline",
            description="Keeps the rewritten post near the intended size instead of bloating or over-compressing it.",
            weight=0.2,
            rationale="Post stylization must preserve practical publication length.",
            recommended_evaluators=["executable_validator", "golden_oracle"],
            required_features=[],
        ),
        _diagnostic_item(
            metric_id="pattern_cleanup_effectiveness",
            title="Pattern cleanup effectiveness",
            description="Diagnoses whether the cleanup stage removed the most visible AI-writing markers.",
            rationale="Points the optimizer to prompt/tool cleanup defects rather than final ranking only.",
            recommended_evaluators=["llm_judge", "executable_validator"],
            target_stage="synthesis",
            required_features=["tool"] if has_tool else [],
        ),
        _diagnostic_item(
            metric_id="proof_context_preservation",
            title="Proof/context preservation",
            description="Diagnoses whether examples, claims and proof cues were preserved through synthesis.",
            rationale="Useful when candidates sound fluent but lose the factual spine of the post.",
            recommended_evaluators=["llm_judge", "golden_oracle"],
            target_stage="synthesis",
            required_features=[],
        ),
        _diagnostic_item(
            metric_id="over_sanitization_risk",
            title="Over-sanitization risk",
            description="Detects when the agent removes too much voice, energy or personality while cleaning AI patterns.",
            rationale="HITL or stricter prompts may be needed when candidates become bland.",
            recommended_evaluators=["llm_judge"],
            target_stage="synthesis" if has_hitl else "final",
            required_features=[],
        ),
    ]


def _comparative_item(
    *,
    metric_id: str,
    title: str,
    description: str,
    weight: float,
    rationale: str,
    recommended_evaluators: list[str],
    required_features: list[str],
) -> dict[str, Any]:
    """Создает proposal item для comparative metric."""

    return {
        "proposal_item_id": f"mpi_{uuid4().hex[:10]}",
        "metric_kind": "comparative",
        "metric_id": metric_id,
        "title": title,
        "description": description,
        "enabled": True,
        "selected": True,
        "weight": weight,
        "required_features": required_features,
        "target_stage": "final",
        "recommended_evaluators": recommended_evaluators,
        "rationale": rationale,
        "compatibility_status": "ready",
        "compatibility_reason": "",
    }


def _diagnostic_item(
    *,
    metric_id: str,
    title: str,
    description: str,
    rationale: str,
    recommended_evaluators: list[str],
    target_stage: str,
    required_features: list[str],
) -> dict[str, Any]:
    """Создает proposal item для diagnostic signal."""

    return {
        "proposal_item_id": f"mpi_{uuid4().hex[:10]}",
        "metric_kind": "diagnostic",
        "metric_id": metric_id,
        "title": title,
        "description": description,
        "enabled": True,
        "selected": True,
        "weight": 0.0,
        "required_features": required_features,
        "target_stage": target_stage,
        "recommended_evaluators": recommended_evaluators,
        "rationale": rationale,
        "compatibility_status": "ready",
        "compatibility_reason": "",
    }


def _build_noop_review_items(*, evaluation_profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Возвращает review-only item, когда новых метрик уже нет."""

    enabled_total = sum(
        1
        for item in [
            *evaluation_profile.get("comparative_metrics", []),
            *evaluation_profile.get("diagnostic_signals", []),
        ]
        if isinstance(item, dict) and bool(item.get("enabled", False))
    )
    return [
        {
            "proposal_item_id": f"mpi_{uuid4().hex[:10]}",
            "metric_kind": "diagnostic",
            "metric_id": "profile_review_note",
            "title": "Profile review note",
            "description": f"Current profile already contains task-specific metrics. Enabled metrics/signals: {enabled_total}.",
            "enabled": False,
            "selected": False,
            "weight": 0.0,
            "required_features": [],
            "target_stage": "final",
            "recommended_evaluators": [],
            "rationale": "No automatic profile mutation is needed.",
            "compatibility_status": "review_only",
            "compatibility_reason": "This item is informational and cannot be applied.",
        }
    ]
