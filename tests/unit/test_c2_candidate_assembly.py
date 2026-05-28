"""Unit-тесты внутреннего этапа подготовки C2 кандидатов к тестам."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.c2 import build_candidate_draft_from_brief, select_candidates_for_tests_and_prepare


def test_select_for_tests_prepares_only_selected_candidates() -> None:
    """Проверяет, что внутренний compile gate выполняется только для выбранных кандидатов."""

    project_root = Path(__file__).resolve().parents[2]
    draft = build_candidate_draft_from_brief(
        arena_id="arena_demo_1",
        brief="Собери кандидатов для стилизатора постов.",
        max_candidates=3,
    )

    prepared = select_candidates_for_tests_and_prepare(
        candidate_set_draft=draft,
        selected_candidate_ids=["cand_direct_llm_v0", "cand_pattern_cleaner_v0"],
        project_root=project_root,
        max_compile_attempts=3,
    )

    assert prepared["compile_gate"]["status"] == "ready"
    assert prepared["compile_gate"]["selected_candidates"] == 2
    assert prepared["compile_gate"]["compiled_candidates"] == 2
    assert prepared["compile_gate"]["ready_candidates"] == 2
    assert prepared["compile_gate"]["failed_candidates"] == 0
    by_id = {candidate["candidate_id"]: candidate for candidate in prepared["candidates"]}
    assert by_id["cand_direct_llm_v0"]["selected_for_tests"] is True
    assert by_id["cand_pattern_cleaner_v0"]["selected_for_tests"] is True
    assert by_id["cand_hybrid_retriever_v0"]["selected_for_tests"] is False
    assert by_id["cand_direct_llm_v0"]["compile_readiness"]["status"] == "ready"
    assert by_id["cand_hybrid_retriever_v0"]["compile_readiness"]["status"] == "draft"


def test_select_for_tests_marks_issue_after_internal_retries() -> None:
    """Проверяет, что issue возвращается только после исчерпания внутренних попыток подготовки."""

    project_root = Path(__file__).resolve().parents[2]
    draft = build_candidate_draft_from_brief(
        arena_id="arena_demo_1",
        brief="Собери кандидатов для стилизатора постов.",
        max_candidates=1,
    )
    draft["candidates"][0]["pattern_ref"] = "style.unknown"
    draft["candidates"][0]["dsl_stub_ref"] = "examples/dsl/missing_file.yaml"

    prepared = select_candidates_for_tests_and_prepare(
        candidate_set_draft=draft,
        selected_candidate_ids=["cand_direct_llm_v0"],
        project_root=project_root,
        max_compile_attempts=3,
    )

    assert prepared["compile_gate"]["status"] == "failed"
    assert prepared["compile_gate"]["failed_candidates"] == 1
    readiness = prepared["candidates"][0]["compile_readiness"]
    assert readiness["status"] == "failed"
    assert readiness["attempts_used"] == 1
    assert readiness["user_visible_issue"] is True
    assert readiness["issues"][0]["severity"] == "error"


def test_select_for_tests_rejects_empty_selection() -> None:
    """Проверяет валидацию, что пользователь должен выбрать хотя бы одного кандидата."""

    project_root = Path(__file__).resolve().parents[2]
    draft = build_candidate_draft_from_brief(
        arena_id="arena_demo_1",
        brief="Собери кандидатов для стилизатора постов.",
        max_candidates=1,
    )

    with pytest.raises(ValueError):
        select_candidates_for_tests_and_prepare(
            candidate_set_draft=draft,
            selected_candidate_ids=[],
            project_root=project_root,
            max_compile_attempts=3,
        )
