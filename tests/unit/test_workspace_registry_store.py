"""Unit-тесты JSON-store workspace/project для C1 vertical slice."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.workspace import WorkspaceRegistryStore


def test_store_creates_workspace_and_lists_it(tmp_path: Path) -> None:
    """Проверяет создание workspace и его возврат в list API."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    created = store.create_workspace(name="support-qa", description="Support experiments")

    workspaces = store.list_workspaces()
    assert len(workspaces) == 1
    assert workspaces[0].workspace_id == created.workspace_id
    assert workspaces[0].name == "support-qa"


def test_store_rejects_duplicate_workspace_name(tmp_path: Path) -> None:
    """Проверяет защиту от дублей workspace с одинаковым именем."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    store.create_workspace(name="support-qa", description="")

    with pytest.raises(ValueError):
        store.create_workspace(name="support-qa", description="")


def test_store_creates_project_and_resolves_get_project(tmp_path: Path) -> None:
    """Проверяет создание project и его выбор по project_id."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    workspace = store.create_workspace(name="support-qa", description="")
    project = store.create_project(workspace_id=workspace.workspace_id, name="support-qa.v1", description="")

    projects = store.list_projects(workspace_id=workspace.workspace_id)
    assert len(projects) == 1
    assert projects[0].project_id == project.project_id

    selected = store.get_project(project_id=project.project_id)
    assert selected.project_id == project.project_id
    assert selected.workspace_id == workspace.workspace_id


def test_store_raises_for_unknown_workspace_or_project(tmp_path: Path) -> None:
    """Проверяет fail-fast поведение для несуществующих workspace/project идентификаторов."""

    store = WorkspaceRegistryStore(store_file=tmp_path / "registry.json")
    with pytest.raises(KeyError):
        store.list_projects(workspace_id="ws_unknown")
    with pytest.raises(KeyError):
        store.get_project(project_id="prj_unknown")

