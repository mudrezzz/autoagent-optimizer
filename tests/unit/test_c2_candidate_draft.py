"""Unit-тесты C2 генератора candidate draft."""

from __future__ import annotations

import pytest

from optimizer.c2 import build_candidate_draft_from_brief


def test_candidate_draft_builder_returns_deterministic_shape() -> None:
    """Проверяет базовый контракт candidate draft и ограничение по числу кандидатов."""

    payload = build_candidate_draft_from_brief(
        arena_id="arena_demo_1",
        brief="Сделай LinkedIn-пост менее шаблонным и более живым.",
        max_candidates=2,
    )

    assert payload["source"] == "c2_brief_to_candidates_v0"
    assert payload["arena_id"] == "arena_demo_1"
    assert payload["total"] == 2
    assert len(payload["candidates"]) == 2
    assert payload["candidates"][0]["candidate_id"] == "cand_direct_llm_v0"
    assert payload["candidates"][0]["logo"]["label"] == "DL"
    assert payload["candidates"][0]["config_summary"]["llm_calls_max"] == 1
    assert payload["candidates"][0]["mini_graph"]["nodes"][1]["label"] == "llm.rewrite"
    assert payload["candidate_set_id"].startswith("cset_")


def test_candidate_draft_builder_rejects_invalid_input() -> None:
    """Проверяет валидацию пустого brief, отсутствия scope-id и некорректного max_candidates."""

    with pytest.raises(ValueError):
        build_candidate_draft_from_brief(arena_id=None, project_id=None, brief="ok", max_candidates=3)
    with pytest.raises(ValueError):
        build_candidate_draft_from_brief(arena_id="arena_demo_1", brief="   ", max_candidates=3)
    with pytest.raises(ValueError):
        build_candidate_draft_from_brief(arena_id="arena_demo_1", brief="ok", max_candidates=0)
    with pytest.raises(ValueError):
        build_candidate_draft_from_brief(arena_id="arena_demo_1", brief="ok", max_candidates=6)
