"""Каталог паттернов C3 и детерминированный поиск с retrieval trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PatternTemplateNode:
    """Узел типовой схемы агента для C3 паттерна."""

    node_id: str
    label: str
    kind: str


@dataclass(frozen=True)
class PatternTemplateEdge:
    """Ребро типовой схемы агента для C3 паттерна."""

    source: str
    target: str


@dataclass(frozen=True)
class PatternTemplate:
    """Типовая схема агента (v0) для паттерна C3."""

    nodes: tuple[PatternTemplateNode, ...]
    edges: tuple[PatternTemplateEdge, ...]
    rationale_steps: tuple[str, ...]


@dataclass(frozen=True)
class PatternConfigSummary:
    """Сводка параметров типовой конфигурации паттерна."""

    roles_total: int
    llm_calls_max: int
    deterministic_guards: int
    hitl_checkpoints: int


@dataclass(frozen=True)
class PatternLogo:
    """Логотип/монограмма паттерна для UI."""

    key: str
    label: str


@dataclass(frozen=True)
class PatternLibraryItem:
    """DTO паттерна библиотеки C3."""

    pattern_id: str
    title: str
    summary: str
    tags: tuple[str, ...]
    complexity: str
    logo: PatternLogo
    config_summary: PatternConfigSummary
    agent_template: PatternTemplate


# Русский комментарий: базовый каталог паттернов v0 для C3-слайса.
PATTERN_LIBRARY: tuple[PatternLibraryItem, ...] = (
    PatternLibraryItem(
        pattern_id="style.direct_llm",
        title="Direct LLM Rewrite",
        summary="Single-pass rewrite with concise instructions and deterministic post-check.",
        tags=("rewrite", "fast", "baseline"),
        complexity="low",
        logo=PatternLogo(key="direct", label="DL"),
        config_summary=PatternConfigSummary(
            roles_total=1,
            llm_calls_max=1,
            deterministic_guards=1,
            hitl_checkpoints=0,
        ),
        agent_template=PatternTemplate(
            nodes=(
                PatternTemplateNode(node_id="input", label="input", kind="input"),
                PatternTemplateNode(node_id="rewrite", label="llm.rewrite", kind="llm"),
                PatternTemplateNode(node_id="guard", label="style.guard", kind="validator"),
                PatternTemplateNode(node_id="output", label="output", kind="output"),
            ),
            edges=(
                PatternTemplateEdge(source="input", target="rewrite"),
                PatternTemplateEdge(source="rewrite", target="guard"),
                PatternTemplateEdge(source="guard", target="output"),
            ),
            rationale_steps=(
                "accept_input",
                "rewrite_llm",
                "style_guard",
                "return_output",
            ),
        ),
    ),
    PatternLibraryItem(
        pattern_id="style.pattern_cleaner",
        title="Pattern Cleaner",
        summary="Two-pass rewrite with explicit cleanup of repetitive AI phrasing.",
        tags=("rewrite", "cleanup", "quality"),
        complexity="medium",
        logo=PatternLogo(key="cleaner", label="PC"),
        config_summary=PatternConfigSummary(
            roles_total=2,
            llm_calls_max=2,
            deterministic_guards=1,
            hitl_checkpoints=0,
        ),
        agent_template=PatternTemplate(
            nodes=(
                PatternTemplateNode(node_id="input", label="input", kind="input"),
                PatternTemplateNode(node_id="draft", label="llm.rewrite", kind="llm"),
                PatternTemplateNode(node_id="cleanup", label="llm.cleanup", kind="llm"),
                PatternTemplateNode(node_id="guard", label="style.guard", kind="validator"),
                PatternTemplateNode(node_id="output", label="output", kind="output"),
            ),
            edges=(
                PatternTemplateEdge(source="input", target="draft"),
                PatternTemplateEdge(source="draft", target="cleanup"),
                PatternTemplateEdge(source="cleanup", target="guard"),
                PatternTemplateEdge(source="guard", target="output"),
            ),
            rationale_steps=(
                "accept_input",
                "rewrite_draft",
                "cleanup_pass",
                "style_guard",
                "return_output",
            ),
        ),
    ),
    PatternLibraryItem(
        pattern_id="style.hitl_reviewer",
        title="HITL Reviewer Gate",
        summary="Adds reviewer checkpoint for borderline outputs and high-risk claims.",
        tags=("rewrite", "safety", "hitl"),
        complexity="high",
        logo=PatternLogo(key="hitl", label="HR"),
        config_summary=PatternConfigSummary(
            roles_total=2,
            llm_calls_max=1,
            deterministic_guards=1,
            hitl_checkpoints=1,
        ),
        agent_template=PatternTemplate(
            nodes=(
                PatternTemplateNode(node_id="input", label="input", kind="input"),
                PatternTemplateNode(node_id="rewrite", label="llm.rewrite", kind="llm"),
                PatternTemplateNode(node_id="score", label="policy.score", kind="tool"),
                PatternTemplateNode(node_id="review", label="hitl.review", kind="hitl"),
                PatternTemplateNode(node_id="guard", label="style.guard", kind="validator"),
                PatternTemplateNode(node_id="output", label="output", kind="output"),
            ),
            edges=(
                PatternTemplateEdge(source="input", target="rewrite"),
                PatternTemplateEdge(source="rewrite", target="score"),
                PatternTemplateEdge(source="score", target="review"),
                PatternTemplateEdge(source="review", target="guard"),
                PatternTemplateEdge(source="guard", target="output"),
            ),
            rationale_steps=(
                "accept_input",
                "rewrite_llm",
                "risk_score",
                "hitl_review",
                "style_guard",
                "return_output",
            ),
        ),
    ),
    PatternLibraryItem(
        pattern_id="style.hybrid_retriever",
        title="Hybrid Retriever Assist",
        summary="Retrieves tone examples before synthesis to preserve narrative structure.",
        tags=("rag", "retrieval", "style"),
        complexity="medium",
        logo=PatternLogo(key="hybrid", label="HRG"),
        config_summary=PatternConfigSummary(
            roles_total=2,
            llm_calls_max=1,
            deterministic_guards=1,
            hitl_checkpoints=0,
        ),
        agent_template=PatternTemplate(
            nodes=(
                PatternTemplateNode(node_id="input", label="input", kind="input"),
                PatternTemplateNode(node_id="retrieve", label="retriever.search", kind="tool"),
                PatternTemplateNode(node_id="rewrite", label="llm.rewrite", kind="llm"),
                PatternTemplateNode(node_id="guard", label="style.guard", kind="validator"),
                PatternTemplateNode(node_id="output", label="output", kind="output"),
            ),
            edges=(
                PatternTemplateEdge(source="input", target="retrieve"),
                PatternTemplateEdge(source="retrieve", target="rewrite"),
                PatternTemplateEdge(source="rewrite", target="guard"),
                PatternTemplateEdge(source="guard", target="output"),
            ),
            rationale_steps=(
                "accept_input",
                "retrieve_style_examples",
                "rewrite_with_context",
                "style_guard",
                "return_output",
            ),
        ),
    ),
    PatternLibraryItem(
        pattern_id="style.structured_editor",
        title="Structured Editor",
        summary="Splits post into structure blocks, rewrites each block, then reassembles.",
        tags=("rewrite", "structure", "planning"),
        complexity="medium",
        logo=PatternLogo(key="editor", label="SE"),
        config_summary=PatternConfigSummary(
            roles_total=3,
            llm_calls_max=2,
            deterministic_guards=1,
            hitl_checkpoints=0,
        ),
        agent_template=PatternTemplate(
            nodes=(
                PatternTemplateNode(node_id="input", label="input", kind="input"),
                PatternTemplateNode(node_id="plan", label="planner.split", kind="tool"),
                PatternTemplateNode(node_id="rewrite", label="llm.rewrite", kind="llm"),
                PatternTemplateNode(node_id="assemble", label="assembler.merge", kind="tool"),
                PatternTemplateNode(node_id="guard", label="style.guard", kind="validator"),
                PatternTemplateNode(node_id="output", label="output", kind="output"),
            ),
            edges=(
                PatternTemplateEdge(source="input", target="plan"),
                PatternTemplateEdge(source="plan", target="rewrite"),
                PatternTemplateEdge(source="rewrite", target="assemble"),
                PatternTemplateEdge(source="assemble", target="guard"),
                PatternTemplateEdge(source="guard", target="output"),
            ),
            rationale_steps=(
                "accept_input",
                "split_into_blocks",
                "rewrite_blocks",
                "merge_blocks",
                "style_guard",
                "return_output",
            ),
        ),
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
                "logo": {"key": item.logo.key, "label": item.logo.label},
                "config_summary": {
                    "roles_total": item.config_summary.roles_total,
                    "llm_calls_max": item.config_summary.llm_calls_max,
                    "deterministic_guards": item.config_summary.deterministic_guards,
                    "hitl_checkpoints": item.config_summary.hitl_checkpoints,
                },
                "agent_template": {
                    "nodes": [
                        {"id": node.node_id, "label": node.label, "kind": node.kind}
                        for node in item.agent_template.nodes
                    ],
                    "edges": [
                        {"source": edge.source, "target": edge.target}
                        for edge in item.agent_template.edges
                    ],
                    "rationale_steps": list(item.agent_template.rationale_steps),
                },
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
