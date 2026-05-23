"""Unit-тесты JSON-store workspace/project для C1 vertical slice."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.workspace import WorkspaceRegistryStore


def test_store_creates_workspace_and_lists_it(tmp_path: Path) -> None:
    """Проверяет создание workspace и его возврат в list API."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    created = store.create_workspace(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="support-qa",
        description="Support experiments",
    )

    workspaces = store.list_workspaces(tenant_id="tenant_a", owner_user_id="user_a")
    assert len(workspaces) == 1
    assert workspaces[0].workspace_id == created.workspace_id
    assert workspaces[0].name == "support-qa"
    assert workspaces[0].tenant_id == "tenant_a"
    assert workspaces[0].owner_user_id == "user_a"


def test_store_rejects_duplicate_workspace_name(tmp_path: Path) -> None:
    """Проверяет защиту от дублей workspace с одинаковым именем."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    store.create_workspace(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")

    with pytest.raises(ValueError):
        store.create_workspace(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")


def test_store_creates_project_and_resolves_get_project(tmp_path: Path) -> None:
    """Проверяет создание project и его выбор по project_id."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    workspace = store.create_workspace(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")
    project = store.create_project(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace.workspace_id,
        name="support-qa.v1",
        description="",
    )

    projects = store.list_projects(tenant_id="tenant_a", owner_user_id="user_a", workspace_id=workspace.workspace_id)
    assert len(projects) == 1
    assert projects[0].project_id == project.project_id

    selected = store.get_project(tenant_id="tenant_a", owner_user_id="user_a", project_id=project.project_id)
    assert selected.project_id == project.project_id
    assert selected.workspace_id == workspace.workspace_id


def test_store_raises_for_unknown_workspace_or_project(tmp_path: Path) -> None:
    """Проверяет fail-fast поведение для несуществующих workspace/project идентификаторов."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    with pytest.raises(KeyError):
        store.list_projects(tenant_id="tenant_a", owner_user_id="user_a", workspace_id="ws_unknown")
    with pytest.raises(KeyError):
        store.get_project(tenant_id="tenant_a", owner_user_id="user_a", project_id="prj_unknown")


def test_store_isolates_records_by_tenant_and_user(tmp_path: Path) -> None:
    """Проверяет tenant/user изоляцию workspace и project записей."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    workspace_a = store.create_workspace(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")
    workspace_b = store.create_workspace(tenant_id="tenant_b", owner_user_id="user_b", name="support-qa", description="")
    store.create_project(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace_a.workspace_id,
        name="support-qa.v1",
        description="",
    )
    store.create_project(
        tenant_id="tenant_b",
        owner_user_id="user_b",
        workspace_id=workspace_b.workspace_id,
        name="support-qa.v1",
        description="",
    )

    workspaces_a = store.list_workspaces(tenant_id="tenant_a", owner_user_id="user_a")
    workspaces_b = store.list_workspaces(tenant_id="tenant_b", owner_user_id="user_b")
    assert len(workspaces_a) == 1
    assert len(workspaces_b) == 1
    assert workspaces_a[0].workspace_id != workspaces_b[0].workspace_id

    projects_a = store.list_projects(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace_a.workspace_id,
    )
    projects_b = store.list_projects(
        tenant_id="tenant_b",
        owner_user_id="user_b",
        workspace_id=workspace_b.workspace_id,
    )
    assert len(projects_a) == 1
    assert len(projects_b) == 1

    with pytest.raises(KeyError):
        store.list_projects(
            tenant_id="tenant_a",
            owner_user_id="user_a",
            workspace_id=workspace_b.workspace_id,
        )


def test_store_renames_workspace_and_rejects_duplicate_name(tmp_path: Path) -> None:
    """Проверяет переименование workspace и защиту от дублирующегося имени."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    first = store.create_workspace(tenant_id="tenant_a", owner_user_id="user_a", name="support-qa", description="")
    store.create_workspace(tenant_id="tenant_a", owner_user_id="user_a", name="billing-qa", description="")

    renamed = store.rename_workspace(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=first.workspace_id,
        name="support-l2",
    )
    assert renamed.name == "support-l2"

    with pytest.raises(ValueError):
        store.rename_workspace(
            tenant_id="tenant_a",
            owner_user_id="user_a",
            workspace_id=first.workspace_id,
            name="billing-qa",
        )


def test_store_duplicates_and_deletes_workspace(tmp_path: Path) -> None:
    """Проверяет дублирование workspace и удаление в пределах tenant/user scope."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    workspace = store.create_workspace(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="support-qa",
        description="Support experiments",
    )
    store.create_project(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace.workspace_id,
        name="support-qa.v1",
        description="",
    )

    duplicated = store.duplicate_workspace(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace.workspace_id,
    )
    assert duplicated.workspace_id != workspace.workspace_id
    assert duplicated.description == workspace.description
    projects_in_copy = store.list_projects(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=duplicated.workspace_id,
    )
    assert projects_in_copy == []

    store.delete_workspace(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace.workspace_id,
    )
    remaining = store.list_workspaces(tenant_id="tenant_a", owner_user_id="user_a")
    assert len(remaining) == 1
    assert remaining[0].workspace_id == duplicated.workspace_id


def test_store_persists_c2_chat_messages_and_candidate_draft(tmp_path: Path) -> None:
    """Проверяет сохранение C2 chat-history и candidate draft в project scope."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    workspace = store.create_workspace(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        name="support-qa",
        description="",
    )
    project = store.create_project(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        workspace_id=workspace.workspace_id,
        name="support-qa.v1",
        description="",
    )

    first_message = store.append_project_chat_message(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        project_id=project.project_id,
        role="user",
        content="Нужно убрать ИИ-паттерны из поста.",
    )
    assert first_message["role"] == "user"
    assert first_message["content"] == "Нужно убрать ИИ-паттерны из поста."

    second_message = store.append_project_chat_message(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        project_id=project.project_id,
        role="assistant",
        content="Сформировал черновик кандидатов.",
    )
    assert second_message["role"] == "assistant"

    history = store.list_project_chat_messages(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        project_id=project.project_id,
    )
    assert len(history) == 2
    assert history[0]["message_id"] != history[1]["message_id"]

    draft_payload = {
        "candidate_set_id": "cset_demo",
        "project_id": project.project_id,
        "total": 2,
        "candidates": [{"candidate_id": "cand_1"}, {"candidate_id": "cand_2"}],
    }
    store.save_project_candidate_set_draft(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        project_id=project.project_id,
        candidate_set_draft=draft_payload,
    )
    loaded_draft = store.get_project_candidate_set_draft(
        tenant_id="tenant_a",
        owner_user_id="user_a",
        project_id=project.project_id,
    )
    assert loaded_draft is not None
    assert loaded_draft["candidate_set_id"] == "cset_demo"
    assert loaded_draft["total"] == 2

    with pytest.raises(KeyError):
        store.list_project_chat_messages(
            tenant_id="tenant_b",
            owner_user_id="user_b",
            project_id=project.project_id,
        )
