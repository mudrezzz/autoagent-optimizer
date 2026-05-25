"""Unit-тесты C3 pattern library и retrieval search."""

from __future__ import annotations

import pytest

from optimizer.c3 import search_pattern_library


def test_search_pattern_library_returns_ranked_payload() -> None:
    """Проверяет базовый ранжированный payload C3 поиска."""

    payload = search_pattern_library(
        query="cleanup rewrite",
        limit=5,
        include_pattern_ids=["style.pattern_cleaner"],
        exclude_pattern_ids=[],
    )

    assert payload["query"] == "cleanup rewrite"
    assert payload["returned"] >= 1
    top = payload["patterns"][0]
    assert top["pattern_id"] == "style.pattern_cleaner"
    assert top["selection_state"] == "include"
    assert any(item.startswith("token:cleanup:") for item in top["retrieval_trace"])
    assert top["logo"]["label"] == "PC"
    assert top["config_summary"]["llm_calls_max"] == 2
    assert top["agent_template"]["nodes"][1]["label"] == "llm.rewrite"
    assert top["agent_template"]["edges"][0]["source"] == "input"
    assert "cleanup_pass" in top["agent_template"]["rationale_steps"]


def test_search_pattern_library_respects_exclude_and_limit() -> None:
    """Проверяет exclude-фильтр и limit в C3 поиске."""

    payload = search_pattern_library(
        query="rewrite",
        limit=1,
        include_pattern_ids=[],
        exclude_pattern_ids=["style.direct_llm"],
    )
    assert payload["returned"] == 1
    assert payload["patterns"][0]["pattern_id"] != "style.direct_llm"


def test_search_pattern_library_rejects_invalid_limit() -> None:
    """Проверяет валидацию limit для C3 поиска."""

    with pytest.raises(ValueError):
        search_pattern_library(query="", limit=0, include_pattern_ids=[], exclude_pattern_ids=[])
