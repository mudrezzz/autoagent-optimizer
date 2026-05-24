"""Каталог паттернов C3 и детерминированный поиск с retrieval trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PatternLibraryItem:
    """DTO паттерна библиотеки C3."""

    pattern_id: str
    title: str
    summary: str
    tags: tuple[str, ...]
    complexity: str


# Русский комментарий: базовый каталог паттернов v0 для C3-слайса.
PATTERN_LIBRARY: tuple[PatternLibraryItem, ...] = (
    PatternLibraryItem(
        pattern_id="style.direct_llm",
        title="Direct LLM Rewrite",
        summary="Single-pass rewrite with concise instructions and deterministic post-check.",
        tags=("rewrite", "fast", "baseline"),
        complexity="low",
    ),
    PatternLibraryItem(
        pattern_id="style.pattern_cleaner",
        title="Pattern Cleaner",
        summary="Two-pass rewrite with explicit cleanup of repetitive AI phrasing.",
        tags=("rewrite", "cleanup", "quality"),
        complexity="medium",
    ),
    PatternLibraryItem(
        pattern_id="style.hitl_reviewer",
        title="HITL Reviewer Gate",
        summary="Adds reviewer checkpoint for borderline outputs and high-risk claims.",
        tags=("rewrite", "safety", "hitl"),
        complexity="high",
    ),
    PatternLibraryItem(
        pattern_id="style.hybrid_retriever",
        title="Hybrid Retriever Assist",
        summary="Retrieves tone examples before synthesis to preserve narrative structure.",
        tags=("rag", "retrieval", "style"),
        complexity="medium",
    ),
    PatternLibraryItem(
        pattern_id="style.structured_editor",
        title="Structured Editor",
        summary="Splits post into structure blocks, rewrites each block, then reassembles.",
        tags=("rewrite", "structure", "planning"),
        complexity="medium",
    ),
)


def search_pattern_library(
    *,
    query: str,
    limit: int,
    include_pattern_ids: list[str] | tuple[str, ...],
    exclude_pattern_ids: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    """Ищет паттерны в библиотеке и возвращает retrieval trace для UI."""

    if limit < 1 or limit > 50:
        raise ValueError("limit must be in range [1, 50].")

    normalized_query = query.strip().lower()
    query_tokens = [token for token in normalized_query.split() if token]
    include_set = {item.strip() for item in include_pattern_ids if item.strip()}
    exclude_set = {item.strip() for item in exclude_pattern_ids if item.strip()}

    ranked: list[tuple[float, PatternLibraryItem, list[str]]] = []
    for item in PATTERN_LIBRARY:
        if item.pattern_id in exclude_set:
            continue
        score, trace = _score_pattern(item=item, query_tokens=query_tokens, include_set=include_set)
        ranked.append((score, item, trace))

    ranked.sort(key=lambda item: (item[0], item[1].pattern_id), reverse=True)
    selected = ranked[:limit]
    patterns_payload: list[dict[str, Any]] = []
    for score, item, trace in selected:
        selection_state = "neutral"
        if item.pattern_id in include_set:
            selection_state = "include"
        elif item.pattern_id in exclude_set:
            selection_state = "exclude"
        patterns_payload.append(
            {
                "pattern_id": item.pattern_id,
                "title": item.title,
                "summary": item.summary,
                "tags": list(item.tags),
                "complexity": item.complexity,
                "relevance": round(score, 3),
                "selection_state": selection_state,
                "retrieval_trace": trace,
            }
        )

    return {
        "query": query,
        "query_tokens": query_tokens,
        "total_candidates": len(ranked),
        "returned": len(patterns_payload),
        "patterns": patterns_payload,
    }


def _score_pattern(*, item: PatternLibraryItem, query_tokens: list[str], include_set: set[str]) -> tuple[float, list[str]]:
    """Считает простой детерминированный score паттерна для C3 v0."""

    score = 0.1
    trace: list[str] = []
    searchable = f"{item.title} {item.summary} {' '.join(item.tags)}".lower()

    if item.pattern_id in include_set:
        score += 0.35
        trace.append("boost:included_by_user")

    if not query_tokens:
        trace.append("query:empty")
        return score, trace

    for token in query_tokens:
        if token in searchable:
            score += 0.22
            trace.append(f"token:{token}:match")
        else:
            trace.append(f"token:{token}:miss")

    return score, trace
