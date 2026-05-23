"""Генератор чернового candidate set для C2 brief-to-candidates v0."""

from __future__ import annotations

from typing import Any


def build_candidate_draft_from_brief(*, project_id: str, brief: str, max_candidates: int = 3) -> dict[str, Any]:
    """Строит детерминированный candidate draft из текстового brief без LLM-зависимости."""

    normalized_brief = brief.strip()
    if not normalized_brief:
        raise ValueError("Brief must be a non-empty string.")
    if max_candidates < 1 or max_candidates > 5:
        raise ValueError("max_candidates must be in range [1, 5].")

    # Русский комментарий: базовые паттерны-кандидаты v0 для демонстрации C2 цикла.
    base_candidates: list[dict[str, Any]] = [
        {
            "candidate_id": "cand_direct_llm_v0",
            "title": "Direct LLM Rewriter",
            "pattern_ref": "style.direct_llm",
            "summary": "Single-agent rewrite path with compact prompt and deterministic post-check.",
            "rationale": "Fast baseline for style transfer with minimal latency.",
            "dsl_stub_ref": "examples/dsl/style_direct_llm.yaml",
            "estimated_complexity": "low",
        },
        {
            "candidate_id": "cand_pattern_cleaner_v0",
            "title": "Pattern Cleaner",
            "pattern_ref": "style.pattern_cleaner",
            "summary": "Two-step rewrite with anti-pattern cleanup pass before final output.",
            "rationale": "Improves removal of repetitive AI phrasing while preserving structure.",
            "dsl_stub_ref": "examples/dsl/style_pattern_cleaner.yaml",
            "estimated_complexity": "medium",
        },
        {
            "candidate_id": "cand_hitl_reviewer_v0",
            "title": "HITL Reviewer Gate",
            "pattern_ref": "style.hitl_reviewer",
            "summary": "Adds reviewer checkpoint for borderline outputs with policy note.",
            "rationale": "Reduces style-regression risk on sensitive posts.",
            "dsl_stub_ref": "examples/dsl/style_hitl_reviewer.yaml",
            "estimated_complexity": "high",
        },
    ]

    selected_candidates = base_candidates[:max_candidates]
    return {
        "candidate_set_id": f"cset_{_stable_suffix(project_id=project_id, brief=normalized_brief)}",
        "source": "c2_brief_to_candidates_v0",
        "task_brief": normalized_brief,
        "generation_mode": "templated_deterministic",
        "project_id": project_id,
        "candidates": selected_candidates,
        "total": len(selected_candidates),
    }


def _stable_suffix(*, project_id: str, brief: str) -> str:
    """Возвращает короткий детерминированный суффикс для candidate_set_id."""

    seed = f"{project_id}:{brief}"
    value = 0
    for char in seed:
        value = (value * 31 + ord(char)) & 0xFFFFFFFF
    return f"{value:08x}"[:8]

