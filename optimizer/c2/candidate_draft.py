"""Генератор чернового candidate set для C2 brief-to-candidates v0."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_candidate_draft_from_brief(
    *,
    arena_id: str | None = None,
    project_id: str | None = None,
    brief: str,
    max_candidates: int = 3,
    preferred_pattern_refs: list[str] | tuple[str, ...] | None = None,
    excluded_pattern_refs: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Строит детерминированный candidate draft из текстового brief без LLM-зависимости."""

    # Русский комментарий: поддерживаем оба ключа scope-id для мягкой миграции project -> arena.
    scope_id = (arena_id or project_id or "").strip()
    if not scope_id:
        raise ValueError("Either `arena_id` or `project_id` must be provided.")

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
            # Русский комментарий: logo и mini-graph используются в C2 accordion деталей на фронтенде.
            "logo": {"key": "direct", "label": "DL"},
            "config_summary": {
                "roles_total": 1,
                "llm_calls_max": 1,
                "deterministic_guards": 1,
                "hitl_checkpoints": 0,
            },
            "architecture_steps": [
                "accept_input",
                "rewrite_llm",
                "style_guard",
                "return_output",
            ],
            "mini_graph": {
                "nodes": [
                    {"id": "accept_input", "label": "input", "kind": "input"},
                    {"id": "rewrite_llm", "label": "llm.rewrite", "kind": "llm"},
                    {"id": "style_guard", "label": "style.guard", "kind": "validator"},
                    {"id": "return_output", "label": "output", "kind": "output"},
                ],
                "edges": [
                    {"source": "accept_input", "target": "rewrite_llm"},
                    {"source": "rewrite_llm", "target": "style_guard"},
                    {"source": "style_guard", "target": "return_output"},
                ],
            },
        },
        {
            "candidate_id": "cand_pattern_cleaner_v0",
            "title": "Pattern Cleaner",
            "pattern_ref": "style.pattern_cleaner",
            "summary": "Two-step rewrite with anti-pattern cleanup pass before final output.",
            "rationale": "Improves removal of repetitive AI phrasing while preserving structure.",
            "dsl_stub_ref": "examples/dsl/style_pattern_cleaner.yaml",
            "estimated_complexity": "medium",
            "logo": {"key": "cleaner", "label": "PC"},
            "config_summary": {
                "roles_total": 2,
                "llm_calls_max": 2,
                "deterministic_guards": 1,
                "hitl_checkpoints": 0,
            },
            "architecture_steps": [
                "accept_input",
                "rewrite_draft",
                "cleanup_pass",
                "style_guard",
                "return_output",
            ],
            "mini_graph": {
                "nodes": [
                    {"id": "accept_input", "label": "input", "kind": "input"},
                    {"id": "rewrite_draft", "label": "llm.rewrite", "kind": "llm"},
                    {"id": "cleanup_pass", "label": "llm.cleanup", "kind": "llm"},
                    {"id": "style_guard", "label": "style.guard", "kind": "validator"},
                    {"id": "return_output", "label": "output", "kind": "output"},
                ],
                "edges": [
                    {"source": "accept_input", "target": "rewrite_draft"},
                    {"source": "rewrite_draft", "target": "cleanup_pass"},
                    {"source": "cleanup_pass", "target": "style_guard"},
                    {"source": "style_guard", "target": "return_output"},
                ],
            },
        },
        {
            "candidate_id": "cand_hybrid_retriever_v0",
            "title": "Hybrid Retriever Assist",
            "pattern_ref": "style.hybrid_retriever",
            "summary": "Retrieval-first rewrite with rerank pass before final synthesis.",
            "rationale": "Adds evidence grounding and ranking diagnostics for RAG-style optimization.",
            "dsl_stub_ref": "examples/dsl/style_hybrid_retriever.yaml",
            "estimated_complexity": "medium",
            "logo": {"key": "hybrid", "label": "HRG"},
            "config_summary": {
                "roles_total": 3,
                "llm_calls_max": 1,
                "deterministic_guards": 1,
                "hitl_checkpoints": 0,
            },
            "architecture_steps": [
                "accept_input",
                "retrieve_examples",
                "rerank_examples",
                "rewrite_with_context",
                "style_guard",
                "return_output",
            ],
            "mini_graph": {
                "nodes": [
                    {"id": "accept_input", "label": "input", "kind": "input"},
                    {"id": "retrieve_examples", "label": "retriever.bm25", "kind": "retriever"},
                    {"id": "rerank_examples", "label": "rerank.cross", "kind": "rerank"},
                    {"id": "rewrite_with_context", "label": "llm.answer", "kind": "llm"},
                    {"id": "style_guard", "label": "style.guard", "kind": "validator"},
                    {"id": "return_output", "label": "output", "kind": "output"},
                ],
                "edges": [
                    {"source": "accept_input", "target": "retrieve_examples"},
                    {"source": "retrieve_examples", "target": "rerank_examples"},
                    {"source": "rerank_examples", "target": "rewrite_with_context"},
                    {"source": "rewrite_with_context", "target": "style_guard"},
                    {"source": "style_guard", "target": "return_output"},
                ],
            },
        },
        {
            "candidate_id": "cand_hitl_reviewer_v0",
            "title": "HITL Reviewer Gate",
            "pattern_ref": "style.hitl_reviewer",
            "summary": "Adds reviewer checkpoint for borderline outputs with policy note.",
            "rationale": "Reduces style-regression risk on sensitive posts.",
            "dsl_stub_ref": "examples/dsl/style_hitl_reviewer.yaml",
            "estimated_complexity": "high",
            "logo": {"key": "hitl", "label": "HR"},
            "config_summary": {
                "roles_total": 2,
                "llm_calls_max": 1,
                "deterministic_guards": 1,
                "hitl_checkpoints": 1,
            },
            "architecture_steps": [
                "accept_input",
                "rewrite_llm",
                "risk_score",
                "hitl_review",
                "style_guard",
                "return_output",
            ],
            "mini_graph": {
                "nodes": [
                    {"id": "accept_input", "label": "input", "kind": "input"},
                    {"id": "rewrite_llm", "label": "llm.rewrite", "kind": "llm"},
                    {"id": "risk_score", "label": "policy.score", "kind": "tool"},
                    {"id": "hitl_review", "label": "hitl.review", "kind": "hitl"},
                    {"id": "style_guard", "label": "style.guard", "kind": "validator"},
                    {"id": "return_output", "label": "output", "kind": "output"},
                ],
                "edges": [
                    {"source": "accept_input", "target": "rewrite_llm"},
                    {"source": "rewrite_llm", "target": "risk_score"},
                    {"source": "risk_score", "target": "hitl_review"},
                    {"source": "hitl_review", "target": "style_guard"},
                    {"source": "style_guard", "target": "return_output"},
                ],
            },
        },
    ]

    include_set = {item.strip() for item in (preferred_pattern_refs or []) if item.strip()}
    exclude_set = {item.strip() for item in (excluded_pattern_refs or []) if item.strip()}
    filtered_candidates: list[dict[str, Any]] = []
    for candidate in base_candidates:
        pattern_ref = str(candidate.get("pattern_ref", ""))
        if pattern_ref in exclude_set:
            continue
        if include_set and pattern_ref not in include_set:
            continue
        filtered_candidates.append(candidate)

    if not filtered_candidates:
        raise ValueError("No candidate templates available after pattern filters.")

    # Русский комментарий: deep-copy нужен, чтобы compile-readiness мутации не затрагивали базовые шаблоны.
    selected_candidates = [deepcopy(candidate) for candidate in filtered_candidates[:max_candidates]]
    for candidate in selected_candidates:
        # Русский комментарий: флаг пользовательского отбора кандидата в тестовый прогон.
        candidate["selected_for_tests"] = False
        # Русский комментарий: стартовый статус кандидата до запуска compile gate.
        candidate["compile_readiness"] = {
            "status": "draft",
            "dsl_file": str(candidate.get("dsl_stub_ref", "")),
            "compile_summary": None,
            "issues": [],
            "graph_ir_summary": {"available": False},
            "compiled_at": None,
        }

    total_selected = len(selected_candidates)
    payload: dict[str, Any] = {
        "candidate_set_id": f"cset_{_stable_suffix(scope_id=scope_id, brief=normalized_brief)}",
        "source": "c2_brief_to_candidates_v0",
        "task_brief": normalized_brief,
        "generation_mode": "templated_deterministic",
        "arena_id": scope_id,
        "candidates": selected_candidates,
        "total": total_selected,
        "source_patterns": [str(candidate["pattern_ref"]) for candidate in selected_candidates],
        "applied_pattern_filters": {
            "include_pattern_refs": sorted(include_set),
            "exclude_pattern_refs": sorted(exclude_set),
        },
        # Русский комментарий: агрегированный readiness-статус набора до первого запуска compile gate.
        "compile_gate": {
            "status": "draft",
            "compiled_candidates": 0,
            "ready_candidates": 0,
            "failed_candidates": 0,
            "selected_candidates": 0,
            "total_candidates": total_selected,
            "processed_at": None,
            "max_compile_attempts": None,
        },
    }
    # Русский комментарий: legacy-поле сохраняем для совместимости старых отчетов/тестов.
    if project_id is not None:
        payload["project_id"] = project_id
    return payload


def _stable_suffix(*, scope_id: str, brief: str) -> str:
    """Возвращает короткий детерминированный суффикс для candidate_set_id."""

    seed = f"{scope_id}:{brief}"
    value = 0
    for char in seed:
        value = (value * 31 + ord(char)) & 0xFFFFFFFF
    return f"{value:08x}"[:8]
