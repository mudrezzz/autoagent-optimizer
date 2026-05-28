"""Unit-тесты JSON-store arena/workspace для C1 и C2 vertical slice."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.workspace import WorkspaceRegistryStore


def test_store_creates_arena_and_lists_it(tmp_path: Path) -> None:
    """Проверяет создание арены и ее возврат в list API."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    created = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="support-qa",
        description="Support experiments",
    )

    arenas = store.list_arenas(tenant_id="tenant_a", owner_user_id="user_a")
    assert len(arenas) == 1
    assert arenas[0].workspace_id == created.workspace_id
    assert arenas[0].name == "support-qa"


def test_store_rejects_duplicate_arena_name(tmp_path: Path) -> None:
    """Проверяет защиту от дублей арен с одинаковым именем."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    store.create_arena(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")

    with pytest.raises(ValueError):
        store.create_arena(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")


def test_store_renames_duplicates_and_deletes_arena(tmp_path: Path) -> None:
    """Проверяет rename/duplicate/delete операции для арен."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="support-qa",
        description="Support experiments",
    )

    renamed = store.rename_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        name="support-qa-renamed",
    )
    assert renamed.name == "support-qa-renamed"

    duplicated = store.duplicate_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert duplicated.workspace_id != arena.workspace_id

    store.delete_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    remaining = store.list_arenas(tenant_id="tenant_a", owner_user_id="user_a")
    assert len(remaining) == 1
    assert remaining[0].workspace_id == duplicated.workspace_id


def test_store_isolates_arenas_by_tenant_and_user(tmp_path: Path) -> None:
    """Проверяет tenant/user изоляцию arena записей."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena_a = store.create_arena(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")
    arena_b = store.create_arena(tenant_id="tenant_b", owner_user_id="user_b", name="support-qa", description="")

    arenas_a = store.list_arenas(tenant_id="tenant_a", owner_user_id="user_a")
    arenas_b = store.list_arenas(tenant_id="tenant_b", owner_user_id="user_b")
    assert len(arenas_a) == 1
    assert len(arenas_b) == 1
    assert arenas_a[0].workspace_id == arena_a.workspace_id
    assert arenas_b[0].workspace_id == arena_b.workspace_id

    with pytest.raises(KeyError):
        store.get_arena(tenant_id="tenant_a", owner_user_id="user_a", arena_id=arena_b.workspace_id)


def test_store_persists_c2_chat_messages_and_candidate_draft_in_arena_scope(tmp_path: Path) -> None:
    """Проверяет сохранение C2 chat-history и candidate draft в arena scope."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="support-qa",
        description="",
    )

    first_message = store.append_arena_chat_message(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        role="user",
        content="Нужно убрать ИИ-паттерны из поста.",
    )
    assert first_message["role"] == "user"

    second_message = store.append_arena_chat_message(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        role="assistant",
        content="Сформировал черновик кандидатов.",
    )
    assert second_message["role"] == "assistant"

    history = store.list_arena_chat_messages(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert len(history) == 2
    assert history[0]["message_id"] != history[1]["message_id"]

    draft_payload = {
        "candidate_set_id": "cset_demo",
        "arena_id": arena.workspace_id,
        "total": 2,
        "candidates": [{"candidate_id": "cand_1"}, {"candidate_id": "cand_2"}],
    }
    store.save_arena_candidate_set_draft(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        candidate_set_draft=draft_payload,
    )
    loaded_draft = store.get_arena_candidate_set_draft(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert loaded_draft is not None
    assert loaded_draft["candidate_set_id"] == "cset_demo"
    assert loaded_draft["total"] == 2

    with pytest.raises(KeyError):
        store.list_arena_chat_messages(
            tenant_id="tenant_b",
            owner_user_id="user_b",
            arena_id=arena.workspace_id,
        )


def test_store_persists_c3_pattern_selection_in_arena_scope(tmp_path: Path) -> None:
    """Проверяет сохранение include/exclude C3 pattern selection в arena scope."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="patterns-lab",
        description="",
    )

    initial_selection = store.get_arena_pattern_selection(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert initial_selection["include_pattern_ids"] == []
    assert initial_selection["exclude_pattern_ids"] == []

    updated_selection = store.save_arena_pattern_selection(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        include_pattern_ids=["style.pattern_cleaner", "style.direct_llm"],
        exclude_pattern_ids=["style.hitl_reviewer"],
    )
    assert updated_selection["include_pattern_ids"] == ["style.pattern_cleaner", "style.direct_llm"]
    assert updated_selection["exclude_pattern_ids"] == ["style.hitl_reviewer"]

    loaded_selection = store.get_arena_pattern_selection(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert loaded_selection["include_pattern_ids"] == ["style.pattern_cleaner", "style.direct_llm"]
    assert loaded_selection["exclude_pattern_ids"] == ["style.hitl_reviewer"]


def test_store_rejects_c3_selection_with_overlap(tmp_path: Path) -> None:
    """Проверяет валидацию include/exclude пересечения для C3 selection."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="patterns-lab",
        description="",
    )

    with pytest.raises(ValueError):
        store.save_arena_pattern_selection(
            tenant_id="tenant_a",
            owner_user_id="user_a",
            arena_id=arena.workspace_id,
            include_pattern_ids=["style.pattern_cleaner"],
            exclude_pattern_ids=["style.pattern_cleaner"],
        )


def test_evaluation_metrics_availability_is_feature_aware_for_non_rag_candidates(tmp_path: Path) -> None:
    """Проверяет auto-availability метрик/сигналов для кандидатов без retrieval/rerank."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="metrics-availability",
        description="",
    )
    store.save_arena_candidate_set_draft(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        candidate_set_draft={
            "candidate_set_id": "cset_demo",
            "arena_id": arena.workspace_id,
            "candidates": [
                {
                    "candidate_id": "cand_llm",
                    "selected_for_tests": True,
                    "mini_graph": {
                        "nodes": [
                            {"id": "in", "label": "input", "kind": "input"},
                            {"id": "rewrite", "label": "llm.rewrite", "kind": "llm"},
                            {"id": "out", "label": "output", "kind": "output"},
                        ]
                    },
                }
            ],
        },
    )

    evaluation_state = store.get_arena_evaluation_studio_state(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert evaluation_state["candidate_features"]["llm"] is True
    assert evaluation_state["candidate_features"]["retrieval"] is False
    assert evaluation_state["candidate_features"]["rerank"] is False
    diagnostics = {item["signal_id"]: item for item in evaluation_state["diagnostic_signals"]}
    assert diagnostics["retrieval_coverage"]["availability_status"] == "unavailable"
    assert diagnostics["retrieval_coverage"]["enabled"] is False
    assert diagnostics["rerank_gain"]["availability_status"] == "unavailable"
    assert diagnostics["rerank_gain"]["enabled"] is False
    assert diagnostics["synthesis_drift"]["availability_status"] == "available"


def test_evaluation_metrics_availability_enables_retrieval_signals_for_rag_candidates(tmp_path: Path) -> None:
    """Проверяет, что retrieval/rerank сигналы доступны при наличии соответствующих узлов."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="metrics-availability-rag",
        description="",
    )
    store.save_arena_candidate_set_draft(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        candidate_set_draft={
            "candidate_set_id": "cset_rag",
            "arena_id": arena.workspace_id,
            "candidates": [
                {
                    "candidate_id": "cand_rag",
                    "selected_for_tests": True,
                    "mini_graph": {
                        "nodes": [
                            {"id": "retrieve", "label": "retriever.bm25", "kind": "retriever"},
                            {"id": "rerank", "label": "rerank.cross", "kind": "rerank"},
                            {"id": "answer", "label": "llm.answer", "kind": "llm"},
                        ]
                    },
                }
            ],
        },
    )

    evaluation_state = store.get_arena_evaluation_studio_state(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    diagnostics = {item["signal_id"]: item for item in evaluation_state["diagnostic_signals"]}
    assert diagnostics["retrieval_coverage"]["availability_status"] == "available"
    assert diagnostics["rerank_gain"]["availability_status"] == "available"


def test_evaluator_metric_matrix_is_present_in_evaluation_state(tmp_path: Path) -> None:
    """Проверяет, что в C4 состоянии есть матрица Evaluator x Metric по умолчанию."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="matrix-default",
        description="",
    )

    evaluation_state = store.get_arena_evaluation_studio_state(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    links = evaluation_state.get("evaluator_metric_links", [])
    assert isinstance(links, list)
    assert len(links) > 0
    assert any(item["metric_kind"] == "comparative" and item["metric_id"] == "quality_f1" for item in links)


def test_evaluation_profile_validation_requires_matrix_coverage(tmp_path: Path) -> None:
    """Проверяет, что validate падает при отсутствии покрытий evaluator x metric."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    arena = store.create_arena(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="matrix-coverage",
        description="",
    )

    evaluation_state = store.get_arena_evaluation_studio_state(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    disabled_links = [
        {
            "evaluator_id": str(item.get("evaluator_id", "")),
            "metric_kind": str(item.get("metric_kind", "")),
            "metric_id": str(item.get("metric_id", "")),
            "enabled": False,
        }
        for item in evaluation_state.get("evaluator_metric_links", [])
        if isinstance(item, dict)
    ]
    store.save_arena_evaluation_evaluator_metric_links(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
        evaluator_metric_links=disabled_links,
    )

    report = store.validate_arena_evaluation_profile(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        arena_id=arena.workspace_id,
    )
    assert report["status"] == "invalid"
    issue_codes = {item["code"] for item in report["issues"]}
    assert "evaluator_metric_coverage_gap" in issue_codes
