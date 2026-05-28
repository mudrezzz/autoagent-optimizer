"""Файловое хранилище workspace/project и arena-сущностей для frontend-слайсов."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class WorkspaceRecord:
    """DTO workspace, который возвращается API-слоем в frontend."""

    workspace_id: str
    name: str
    description: str
    created_at: str
    tenant_id: str
    owner_user_id: str


@dataclass(frozen=True)
class ProjectRecord:
    """DTO project, который возвращается API-слоем в frontend."""

    project_id: str
    workspace_id: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str
    tenant_id: str
    owner_user_id: str


class WorkspaceRegistryStore:
    """Потокобезопасный JSON-store workspace/project и arena домена."""

    def __init__(self, store_file: Path) -> None:
        """Инициализирует store и создает директорию/файл при первом запуске."""

        self._store_file = store_file
        self._lock = threading.Lock()
        self._store_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._store_file.exists():
            self._write_store({"version": "workspace_registry_v1", "workspaces": []})

    def list_workspaces(self, *, tenant_id: str, owner_user_id: str) -> list[WorkspaceRecord]:
        """Возвращает tenant/user-scoped workspace без вложенных project-полей."""

        with self._lock:
            data = self._read_store()
            records: list[WorkspaceRecord] = []
            for item in data.get("workspaces", []):
                if str(item.get("tenant_id", "")) != tenant_id or str(item.get("owner_user_id", "")) != owner_user_id:
                    continue
                records.append(self._workspace_to_record(item))
            return records

    def create_workspace(self, *, tenant_id: str, owner_user_id: str, name: str, description: str) -> WorkspaceRecord:
        """Создает новый workspace и сохраняет его в JSON-store."""

        normalized_name = name.strip()
        normalized_description = description.strip()
        if not normalized_name:
            raise ValueError("Workspace name must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            self._assert_unique_workspace_name(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                name=normalized_name,
            )
            now = _utc_now_iso()
            workspace = {
                "workspace_id": f"ws_{uuid4().hex[:10]}",
                "name": normalized_name,
                "description": normalized_description,
                "created_at": now,
                "tenant_id": tenant_id,
                "owner_user_id": owner_user_id,
                "projects": [],
                "chat_messages": [],
                "candidate_set_draft": None,
                "pattern_selection": _build_default_pattern_selection(),
                "dataset_studio": _build_default_dataset_studio_state(),
                "evaluation_studio": _build_default_evaluation_studio_state(),
                "optimizer_studio": _build_default_optimizer_studio_state(),
            }
            data["workspaces"].append(workspace)
            self._write_store(data)
            return self._workspace_to_record(workspace)

    def rename_workspace(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        workspace_id: str,
        name: str,
    ) -> WorkspaceRecord:
        """Переименовывает workspace в рамках tenant/user scope."""

        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Workspace name must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=workspace_id,
            )
            for item in data.get("workspaces", []):
                if (
                    str(item.get("workspace_id")) != workspace_id
                    and str(item.get("tenant_id", "")) == tenant_id
                    and str(item.get("owner_user_id", "")) == owner_user_id
                    and str(item.get("name", "")).strip().lower() == normalized_name.lower()
                ):
                    raise ValueError("Workspace with the same name already exists.")
            workspace["name"] = normalized_name
            self._write_store(data)
            return self._workspace_to_record(workspace)

    def duplicate_workspace(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        workspace_id: str,
        name: str | None = None,
    ) -> WorkspaceRecord:
        """Дублирует workspace (без project-данных) в том же tenant/user scope."""

        with self._lock:
            data = self._read_store()
            source_workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=workspace_id,
            )
            existing_names = {
                str(item.get("name", "")).strip().lower()
                for item in data.get("workspaces", [])
                if str(item.get("tenant_id", "")) == tenant_id and str(item.get("owner_user_id", "")) == owner_user_id
            }
            if name is not None:
                normalized_name = name.strip()
                if not normalized_name:
                    raise ValueError("Workspace name must be a non-empty string.")
                if normalized_name.lower() in existing_names:
                    raise ValueError("Workspace with the same name already exists.")
            else:
                normalized_name = _make_unique_workspace_copy_name(
                    source_name=str(source_workspace.get("name", "")),
                    existing_names=existing_names,
                )

            now = _utc_now_iso()
            workspace_copy = {
                "workspace_id": f"ws_{uuid4().hex[:10]}",
                "name": normalized_name,
                "description": str(source_workspace.get("description", "")),
                "created_at": now,
                "tenant_id": tenant_id,
                "owner_user_id": owner_user_id,
                "projects": [],
                "chat_messages": [],
                "candidate_set_draft": None,
                "pattern_selection": _build_default_pattern_selection(),
                "dataset_studio": _build_default_dataset_studio_state(),
                "evaluation_studio": _build_default_evaluation_studio_state(),
                "optimizer_studio": _build_default_optimizer_studio_state(),
            }
            data["workspaces"].append(workspace_copy)
            self._write_store(data)
            return self._workspace_to_record(workspace_copy)

    def delete_workspace(self, *, tenant_id: str, owner_user_id: str, workspace_id: str) -> None:
        """Удаляет workspace вместе с вложенными project в tenant/user scope."""

        with self._lock:
            data = self._read_store()
            workspaces = data.get("workspaces", [])
            for index, item in enumerate(workspaces):
                if (
                    str(item.get("workspace_id")) == workspace_id
                    and str(item.get("tenant_id", "")) == tenant_id
                    and str(item.get("owner_user_id", "")) == owner_user_id
                ):
                    del workspaces[index]
                    data["workspaces"] = workspaces
                    self._write_store(data)
                    return
        raise KeyError(f"Workspace not found: {workspace_id}")

    def list_projects(self, *, tenant_id: str, owner_user_id: str, workspace_id: str) -> list[ProjectRecord]:
        """Возвращает все project выбранного workspace."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=workspace_id,
            )
            projects = workspace.get("projects", [])
            return [
                self._project_to_record(item)
                for item in projects
                if isinstance(item, dict)
                and str(item.get("tenant_id", "")) == tenant_id
                and str(item.get("owner_user_id", "")) == owner_user_id
            ]

    def create_project(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        workspace_id: str,
        name: str,
        description: str,
    ) -> ProjectRecord:
        """Создает project внутри workspace и обновляет JSON-store."""

        normalized_name = name.strip()
        normalized_description = description.strip()
        if not normalized_name:
            raise ValueError("Project name must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=workspace_id,
            )
            projects = workspace.get("projects", [])
            for item in projects:
                if isinstance(item, dict) and str(item.get("name", "")).strip().lower() == normalized_name.lower():
                    raise ValueError("Project with the same name already exists in workspace.")

            now = _utc_now_iso()
            project = {
                "project_id": f"prj_{uuid4().hex[:10]}",
                "workspace_id": workspace_id,
                "name": normalized_name,
                "description": normalized_description,
                "status": "draft",
                "created_at": now,
                "updated_at": now,
                "tenant_id": tenant_id,
                "owner_user_id": owner_user_id,
                "chat_messages": [],
                "candidate_set_draft": None,
            }
            projects.append(project)
            workspace["projects"] = projects
            self._write_store(data)
            return self._project_to_record(project)

    def get_project(self, *, tenant_id: str, owner_user_id: str, project_id: str) -> ProjectRecord:
        """Возвращает tenant/user-scoped project по идентификатору."""

        with self._lock:
            data = self._read_store()
            project = self._find_project(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                project_id=project_id,
            )
            return self._project_to_record(project)

    def list_project_chat_messages(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        project_id: str,
    ) -> list[dict[str, Any]]:
        """Возвращает историю chat-сообщений проекта для C2."""

        with self._lock:
            data = self._read_store()
            project = self._find_project(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                project_id=project_id,
            )
            return _serialize_messages(project.get("chat_messages", []))

    def append_project_chat_message(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        project_id: str,
        role: str,
        content: str,
    ) -> dict[str, Any]:
        """Добавляет chat-сообщение в проект C2."""

        with self._lock:
            data = self._read_store()
            project = self._find_project(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                project_id=project_id,
            )
            message = _build_message(role=role, content=content)
            messages = project.get("chat_messages", [])
            if not isinstance(messages, list):
                messages = []
            messages.append(message)
            project["chat_messages"] = messages
            project["updated_at"] = _utc_now_iso()
            self._write_store(data)
            return _serialize_message(message)

    def save_project_candidate_set_draft(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        project_id: str,
        candidate_set_draft: dict[str, Any],
    ) -> dict[str, Any]:
        """Сохраняет candidate_set_draft в проекте."""

        if not isinstance(candidate_set_draft, dict):
            raise ValueError("candidate_set_draft must be an object.")

        with self._lock:
            data = self._read_store()
            project = self._find_project(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                project_id=project_id,
            )
            project["candidate_set_draft"] = candidate_set_draft
            project["updated_at"] = _utc_now_iso()
            self._write_store(data)
            return dict(candidate_set_draft)

    def get_project_candidate_set_draft(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        project_id: str,
    ) -> dict[str, Any] | None:
        """Возвращает candidate_set_draft проекта либо None."""

        with self._lock:
            data = self._read_store()
            project = self._find_project(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                project_id=project_id,
            )
            draft = project.get("candidate_set_draft")
            if draft is None or not isinstance(draft, dict):
                return None
            return dict(draft)

    def list_arenas(self, *, tenant_id: str, owner_user_id: str) -> list[WorkspaceRecord]:
        """Возвращает tenant/user-scoped список арен (battle-проектов)."""

        return self.list_workspaces(tenant_id=tenant_id, owner_user_id=owner_user_id)

    def create_arena(self, *, tenant_id: str, owner_user_id: str, name: str, description: str) -> WorkspaceRecord:
        """Создает новую арену (battle-проект) в tenant/user scope."""

        return self.create_workspace(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            name=name,
            description=description,
        )

    def rename_arena(self, *, tenant_id: str, owner_user_id: str, arena_id: str, name: str) -> WorkspaceRecord:
        """Переименовывает арену и возвращает обновленную запись."""

        return self.rename_workspace(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            workspace_id=arena_id,
            name=name,
        )

    def duplicate_arena(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        name: str | None = None,
    ) -> WorkspaceRecord:
        """Дублирует арену без проектных дочерних сущностей."""

        return self.duplicate_workspace(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            workspace_id=arena_id,
            name=name,
        )

    def delete_arena(self, *, tenant_id: str, owner_user_id: str, arena_id: str) -> None:
        """Удаляет арену в рамках tenant/user scope."""

        self.delete_workspace(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            workspace_id=arena_id,
        )

    def get_arena(self, *, tenant_id: str, owner_user_id: str, arena_id: str) -> WorkspaceRecord:
        """Возвращает арену по идентификатору в tenant/user scope."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            return self._workspace_to_record(workspace)

    def list_arena_chat_messages(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> list[dict[str, Any]]:
        """Возвращает историю chat-сообщений арены."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            return _serialize_messages(workspace.get("chat_messages", []))

    def append_arena_chat_message(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        role: str,
        content: str,
    ) -> dict[str, Any]:
        """Добавляет chat-сообщение в арену и возвращает созданную запись."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            message = _build_message(role=role, content=content)
            messages = workspace.get("chat_messages", [])
            if not isinstance(messages, list):
                messages = []
            messages.append(message)
            workspace["chat_messages"] = messages
            self._write_store(data)
            return _serialize_message(message)

    def save_arena_candidate_set_draft(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        candidate_set_draft: dict[str, Any],
    ) -> dict[str, Any]:
        """Сохраняет candidate_set_draft на уровне арены."""

        if not isinstance(candidate_set_draft, dict):
            raise ValueError("candidate_set_draft must be an object.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            workspace["candidate_set_draft"] = candidate_set_draft
            # Русский комментарий: при изменении candidate draft сразу пересчитываем availability метрик C5/C6.
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=candidate_set_draft,
            )
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(candidate_set_draft)

    def get_arena_candidate_set_draft(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> dict[str, Any] | None:
        """Возвращает candidate_set_draft арены либо None."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            draft = workspace.get("candidate_set_draft")
            if draft is None or not isinstance(draft, dict):
                return None
            return dict(draft)

    def get_arena_pattern_selection(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> dict[str, Any]:
        """Возвращает include/exclude выборку паттернов C3 для арены."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            selection = workspace.get("pattern_selection")
            normalized = _normalize_pattern_selection(selection)
            workspace["pattern_selection"] = normalized
            self._write_store(data)
            return dict(normalized)

    def save_arena_pattern_selection(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        include_pattern_ids: list[str],
        exclude_pattern_ids: list[str],
    ) -> dict[str, Any]:
        """Сохраняет include/exclude выборку паттернов C3 для арены."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            normalized = _normalize_pattern_selection(
                {
                    "include_pattern_ids": include_pattern_ids,
                    "exclude_pattern_ids": exclude_pattern_ids,
                    "updated_at": _utc_now_iso(),
                }
            )
            workspace["pattern_selection"] = normalized
            self._write_store(data)
            return dict(normalized)

    def get_arena_dataset_studio_state(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> dict[str, Any]:
        """Возвращает состояние Dataset Studio для выбранной арены."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            normalized_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            workspace["dataset_studio"] = normalized_state
            self._write_store(data)
            return dict(normalized_state)

    def create_arena_dataset(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        name: str,
        description: str,
    ) -> dict[str, Any]:
        """Создает новый dataset в Dataset Studio арены и делает его активным."""

        normalized_name = name.strip()
        normalized_description = description.strip()
        if not normalized_name:
            raise ValueError("Dataset name must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            datasets = studio_state.get("datasets", [])
            if any(str(item.get("name", "")).strip().lower() == normalized_name.lower() for item in datasets):
                raise ValueError("Dataset with the same name already exists.")
            now = _utc_now_iso()
            dataset = {
                "dataset_id": f"dset_{uuid4().hex[:10]}",
                "name": normalized_name,
                "description": normalized_description,
                "created_at": now,
                "updated_at": now,
                "rows": [],
                "versions": [],
            }
            datasets.append(dataset)
            studio_state["datasets"] = datasets
            studio_state["active_dataset_id"] = dataset["dataset_id"]
            workspace["dataset_studio"] = studio_state
            self._write_store(data)
            return dict(dataset)

    def set_active_arena_dataset(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        dataset_id: str,
    ) -> dict[str, Any]:
        """Устанавливает активный dataset для выбранной арены."""

        normalized_dataset_id = dataset_id.strip()
        if not normalized_dataset_id:
            raise ValueError("Dataset id must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            datasets = studio_state.get("datasets", [])
            if not any(str(item.get("dataset_id", "")) == normalized_dataset_id for item in datasets):
                raise KeyError(f"Dataset not found: {normalized_dataset_id}")
            studio_state["active_dataset_id"] = normalized_dataset_id
            workspace["dataset_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def save_arena_assigned_datasets(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        dataset_ids: list[str],
    ) -> dict[str, Any]:
        """Сохраняет выбранный пользователем набор dataset для прогона арены."""

        normalized_dataset_ids = _normalize_dataset_id_list(dataset_ids)
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            known_dataset_ids = {str(item.get("dataset_id", "")) for item in studio_state.get("datasets", [])}
            unknown_dataset_ids = [item for item in normalized_dataset_ids if item not in known_dataset_ids]
            if unknown_dataset_ids:
                raise KeyError(f"Dataset not found: {unknown_dataset_ids[0]}")
            studio_state["assigned_dataset_ids"] = normalized_dataset_ids
            workspace["dataset_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def append_arena_dataset_row(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        dataset_id: str,
        row: dict[str, Any],
    ) -> dict[str, Any]:
        """Добавляет одну строку в dataset и возвращает нормализованную запись."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            dataset = _find_dataset_by_id(studio_state=studio_state, dataset_id=dataset_id)
            normalized_row = _normalize_dataset_row(row)
            rows = dataset.get("rows", [])
            rows.append(normalized_row)
            dataset["rows"] = rows
            dataset["updated_at"] = _utc_now_iso()
            workspace["dataset_studio"] = studio_state
            self._write_store(data)
            return dict(normalized_row)

    def replace_arena_dataset_rows(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        dataset_id: str,
        rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Полностью заменяет строки dataset и возвращает обновленный dataset."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            dataset = _find_dataset_by_id(studio_state=studio_state, dataset_id=dataset_id)
            normalized_rows = [_normalize_dataset_row(item) for item in rows]
            dataset["rows"] = normalized_rows
            dataset["updated_at"] = _utc_now_iso()
            workspace["dataset_studio"] = studio_state
            self._write_store(data)
            return dict(dataset)

    def save_arena_dataset_version(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        dataset_id: str,
        label: str,
        source: str,
    ) -> dict[str, Any]:
        """Сохраняет version snapshot выбранного dataset."""

        normalized_label = label.strip() or f"snapshot-{_utc_now_iso()}"
        normalized_source = source.strip() or "manual"
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            dataset = _find_dataset_by_id(studio_state=studio_state, dataset_id=dataset_id)
            rows = [_normalize_dataset_row(item) for item in dataset.get("rows", [])]
            version = {
                "version_id": f"dsv_{uuid4().hex[:10]}",
                "label": normalized_label,
                "created_at": _utc_now_iso(),
                "rows_total": len(rows),
                "source": normalized_source,
                "rows_snapshot": rows,
            }
            versions = dataset.get("versions", [])
            versions.append(version)
            dataset["versions"] = versions
            dataset["updated_at"] = _utc_now_iso()
            workspace["dataset_studio"] = studio_state
            self._write_store(data)
            return dict(version)

    def validate_arena_dataset(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        dataset_id: str,
    ) -> dict[str, Any]:
        """Выполняет stage-aware валидацию dataset v2 и возвращает отчет issues."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            dataset = _find_dataset_by_id(studio_state=studio_state, dataset_id=dataset_id)
            rows = [_normalize_dataset_row(item) for item in dataset.get("rows", [])]
            issues: list[dict[str, Any]] = []
            seen_case_ids: set[str] = set()
            for index, row in enumerate(rows):
                case_id = str(row.get("case_id", "")).strip()
                input_text = str(row.get("input", "")).strip()
                target_stage = str(row.get("target_stage", "final")).strip().lower() or "final"
                expected_payload = row.get("expected_payload", {})
                if not case_id:
                    issues.append({"severity": "error", "code": "missing_case_id", "row_index": index, "message": "case_id is required."})
                elif case_id in seen_case_ids:
                    issues.append(
                        {"severity": "error", "code": "duplicate_case_id", "row_index": index, "message": f"case_id `{case_id}` is duplicated."}
                    )
                seen_case_ids.add(case_id)
                if not input_text:
                    issues.append({"severity": "error", "code": "missing_input", "row_index": index, "message": "input is required."})
                if target_stage not in _DATASET_TARGET_STAGES:
                    issues.append(
                        {
                            "severity": "error",
                            "code": "invalid_target_stage",
                            "row_index": index,
                            "message": f"target_stage must be one of: {', '.join(_DATASET_TARGET_STAGES)}.",
                        }
                    )
                    continue
                if not isinstance(expected_payload, dict):
                    issues.append(
                        {
                            "severity": "error",
                            "code": "invalid_expected_payload",
                            "row_index": index,
                            "message": "expected_payload must be an object.",
                        }
                    )
                    continue
                if target_stage == "retrieval":
                    evidence_ids = _normalize_string_list(expected_payload.get("evidence_ids", []))
                    if not evidence_ids:
                        issues.append(
                            {
                                "severity": "warning",
                                "code": "missing_expected_retrieval",
                                "row_index": index,
                                "message": "retrieval target should define `expected_payload.evidence_ids`.",
                            }
                        )
                elif target_stage == "rerank":
                    ranked_ids = _normalize_string_list(expected_payload.get("ranked_ids", []))
                    if not ranked_ids:
                        issues.append(
                            {
                                "severity": "warning",
                                "code": "missing_expected_rerank",
                                "row_index": index,
                                "message": "rerank target should define `expected_payload.ranked_ids`.",
                            }
                        )
                elif target_stage == "synthesis":
                    must_include = _normalize_string_list(expected_payload.get("must_include", []))
                    if not must_include:
                        issues.append(
                            {
                                "severity": "warning",
                                "code": "missing_expected_synthesis",
                                "row_index": index,
                                "message": "synthesis target should define `expected_payload.must_include`.",
                            }
                        )
                else:
                    answer = str(expected_payload.get("answer", "")).strip()
                    if not answer:
                        issues.append(
                            {
                                "severity": "warning",
                                "code": "missing_expected_final",
                                "row_index": index,
                                "message": "final target should define non-empty `expected_payload.answer`.",
                            }
                        )

            if not rows:
                issues.append({"severity": "error", "code": "empty_dataset", "row_index": None, "message": "Dataset must contain at least one row."})

            return {
                "dataset_id": str(dataset.get("dataset_id", "")),
                "rows_total": len(rows),
                "issues": issues,
                "status": "ok" if not any(item.get("severity") == "error" for item in issues) else "failed",
            }

    def get_arena_evaluation_studio_state(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> dict[str, Any]:
        """Возвращает состояние C4 Metrics & Evaluators Studio для выбранной арены."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            normalized_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            _sync_evaluation_profile_availability(
                studio_state=normalized_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
            )
            workspace["evaluation_studio"] = normalized_state
            self._write_store(data)
            return dict(normalized_state)

    def save_arena_evaluation_metrics(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        comparative_metrics: list[dict[str, Any]],
        diagnostic_signals: list[dict[str, Any]],
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Сохраняет блок comparative/diagnostic метрик evaluation profile."""

        normalized_comparative_metrics = _normalize_comparative_metrics(comparative_metrics)
        normalized_diagnostic_signals = _normalize_diagnostic_signals(diagnostic_signals)
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            target_profile = _find_target_evaluation_profile(
                studio_state=studio_state,
                profile_id=profile_id,
            )
            target_profile["comparative_metrics"] = normalized_comparative_metrics
            target_profile["diagnostic_signals"] = normalized_diagnostic_signals
            target_profile["updated_at"] = _utc_now_iso()
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
                profile_id=profile_id,
            )
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def save_arena_evaluation_evaluators(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        evaluators: list[dict[str, Any]],
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Сохраняет блок evaluator-адаптеров evaluation profile."""

        normalized_evaluators = _normalize_evaluators(evaluators)
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            target_profile = _find_target_evaluation_profile(
                studio_state=studio_state,
                profile_id=profile_id,
            )
            target_profile["evaluators"] = normalized_evaluators
            target_profile["updated_at"] = _utc_now_iso()
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
                profile_id=profile_id,
            )
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def save_arena_evaluation_evaluator_metric_links(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        evaluator_metric_links: list[dict[str, Any]],
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Сохраняет матрицу связей Evaluator x Metric для evaluation profile."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            target_profile = _find_target_evaluation_profile(
                studio_state=studio_state,
                profile_id=profile_id,
            )
            target_profile["evaluator_metric_links"] = _normalize_evaluator_metric_links(
                raw_links=evaluator_metric_links,
                comparative_metrics=target_profile.get("comparative_metrics", []),
                diagnostic_signals=target_profile.get("diagnostic_signals", []),
                evaluators=target_profile.get("evaluators", []),
            )
            target_profile["updated_at"] = _utc_now_iso()
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
                profile_id=profile_id,
            )
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def save_arena_evaluation_budget(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        budget: dict[str, Any],
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Сохраняет бюджетные ограничения evaluation profile."""

        normalized_budget = _normalize_evaluation_budget(budget)
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            target_profile = _find_target_evaluation_profile(
                studio_state=studio_state,
                profile_id=profile_id,
            )
            target_profile["budget"] = normalized_budget
            target_profile["updated_at"] = _utc_now_iso()
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
                profile_id=profile_id,
            )
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def validate_arena_evaluation_profile(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Выполняет базовую проверку evaluation profile и возвращает issues-репорт."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
                profile_id=profile_id,
            )
            target_profile = _find_target_evaluation_profile(
                studio_state=studio_state,
                profile_id=profile_id,
            )
            return _build_evaluation_profile_validation_report(profile=target_profile)

    def save_arena_evaluation_version(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        label: str,
        source: str,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Сохраняет snapshot-версию evaluation profile."""

        normalized_label = label.strip() or f"snapshot-{_utc_now_iso()}"
        normalized_source = source.strip() or "manual"
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            target_profile = _find_target_evaluation_profile(
                studio_state=studio_state,
                profile_id=profile_id,
            )
            version = {
                "version_id": f"evv_{uuid4().hex[:10]}",
                "label": normalized_label,
                "created_at": _utc_now_iso(),
                "source": normalized_source,
                "comparative_metrics": [dict(item) for item in target_profile.get("comparative_metrics", [])],
                "diagnostic_signals": [dict(item) for item in target_profile.get("diagnostic_signals", [])],
                "evaluators": [dict(item) for item in target_profile.get("evaluators", [])],
                "evaluator_metric_links": [dict(item) for item in target_profile.get("evaluator_metric_links", [])],
                "budget": dict(target_profile.get("budget", {})),
            }
            versions = target_profile.get("versions", [])
            versions.append(version)
            target_profile["versions"] = versions
            target_profile["updated_at"] = _utc_now_iso()
            _sync_evaluation_profile_availability(
                studio_state=studio_state,
                candidate_set_draft=workspace.get("candidate_set_draft") if isinstance(workspace.get("candidate_set_draft"), dict) else None,
                profile_id=profile_id,
            )
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(version)

    def create_arena_evaluation_profile(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        name: str,
        description: str,
    ) -> dict[str, Any]:
        """Создает новый metrics-profile в C4 Metrics Studio и делает его активным."""

        normalized_name = name.strip()
        normalized_description = description.strip()
        if not normalized_name:
            raise ValueError("Evaluation profile name must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            profiles = studio_state.get("profiles", [])
            if any(str(item.get("name", "")).strip().lower() == normalized_name.lower() for item in profiles):
                raise ValueError("Evaluation profile with the same name already exists.")
            profile = _build_default_evaluation_profile(
                profile_id=f"ep_{uuid4().hex[:10]}",
                name=normalized_name,
                description=normalized_description,
            )
            profiles.append(profile)
            studio_state["profiles"] = profiles
            studio_state["active_profile_id"] = str(profile.get("profile_id", ""))
            studio_state["assigned_profile_ids"] = _normalize_evaluation_profile_id_list(
                [*studio_state.get("assigned_profile_ids", []), studio_state["active_profile_id"]]
            )
            _sync_evaluation_studio_legacy_mirror_fields(studio_state)
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(profile)

    def set_active_arena_evaluation_profile(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        profile_id: str,
    ) -> dict[str, Any]:
        """Устанавливает активный metrics-profile для выбранной арены."""

        normalized_profile_id = profile_id.strip()
        if not normalized_profile_id:
            raise ValueError("Evaluation profile id must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            _find_evaluation_profile_by_id(studio_state=studio_state, profile_id=normalized_profile_id)
            studio_state["active_profile_id"] = normalized_profile_id
            _sync_evaluation_studio_legacy_mirror_fields(studio_state)
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def save_arena_assigned_evaluation_profiles(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        profile_ids: list[str],
    ) -> dict[str, Any]:
        """Сохраняет выбранный пользователем набор metrics-profile для арены."""

        normalized_profile_ids = _normalize_evaluation_profile_id_list(profile_ids)
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            known_profile_ids = {str(item.get("profile_id", "")) for item in studio_state.get("profiles", [])}
            unknown_profile_ids = [item for item in normalized_profile_ids if item not in known_profile_ids]
            if unknown_profile_ids:
                raise KeyError(f"Evaluation profile not found: {unknown_profile_ids[0]}")
            studio_state["assigned_profile_ids"] = normalized_profile_ids
            studio_state["updated_at"] = _utc_now_iso()
            workspace["evaluation_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def get_arena_optimizer_studio_state(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> dict[str, Any]:
        """Возвращает состояние C5 Optimizer Setup Studio для выбранной арены."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            normalized_state = _normalize_optimizer_studio_state(workspace.get("optimizer_studio"))
            workspace["optimizer_studio"] = normalized_state
            self._write_store(data)
            return dict(normalized_state)

    def save_arena_optimizer_setup(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        methods: list[dict[str, Any]],
        controls: list[dict[str, Any]],
        run_plan: dict[str, Any],
        budget: dict[str, Any],
    ) -> dict[str, Any]:
        """Сохраняет конфигурацию optimizer setup (methods/controls/run-plan/budget)."""

        normalized_methods = _normalize_optimizer_methods(methods)
        normalized_controls = _normalize_optimizer_controls(controls)
        normalized_run_plan = _normalize_optimizer_run_plan(run_plan)
        normalized_budget = _normalize_optimizer_budget(budget)
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_optimizer_studio_state(workspace.get("optimizer_studio"))
            studio_state["methods"] = normalized_methods
            studio_state["controls"] = normalized_controls
            studio_state["run_plan"] = normalized_run_plan
            studio_state["budget"] = normalized_budget
            studio_state["updated_at"] = _utc_now_iso()
            workspace["optimizer_studio"] = studio_state
            self._write_store(data)
            return dict(studio_state)

    def validate_arena_optimizer_setup(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
    ) -> dict[str, Any]:
        """Валидирует C5 optimizer setup и возвращает guardrail-отчет готовности запуска."""

        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            optimizer_state = _normalize_optimizer_studio_state(workspace.get("optimizer_studio"))
            dataset_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            evaluation_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            candidate_set_draft = workspace.get("candidate_set_draft")
            issues = _build_optimizer_setup_issues(
                optimizer_state=optimizer_state,
                dataset_state=dataset_state,
                evaluation_state=evaluation_state,
                candidate_set_draft=candidate_set_draft if isinstance(candidate_set_draft, dict) else None,
            )
            status = "ready"
            if any(item.get("severity") == "error" for item in issues):
                status = "invalid"
            elif issues:
                status = "warnings"
            return {
                "status": status,
                "issues": issues,
                "updated_at": str(optimizer_state.get("updated_at", "")),
            }

    def save_arena_optimizer_version(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        label: str,
        source: str,
    ) -> dict[str, Any]:
        """Сохраняет snapshot-версию optimizer setup профиля."""

        normalized_label = label.strip() or f"snapshot-{_utc_now_iso()}"
        normalized_source = source.strip() or "manual"
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            studio_state = _normalize_optimizer_studio_state(workspace.get("optimizer_studio"))
            version = {
                "version_id": f"opv_{uuid4().hex[:10]}",
                "label": normalized_label,
                "created_at": _utc_now_iso(),
                "source": normalized_source,
                "methods": [dict(item) for item in studio_state.get("methods", [])],
                "controls": [dict(item) for item in studio_state.get("controls", [])],
                "run_plan": dict(studio_state.get("run_plan", {})),
                "budget": dict(studio_state.get("budget", {})),
            }
            versions = studio_state.get("versions", [])
            versions.append(version)
            studio_state["versions"] = versions
            studio_state["updated_at"] = _utc_now_iso()
            workspace["optimizer_studio"] = studio_state
            self._write_store(data)
            return dict(version)

    def launch_arena_optimizer_run(
        self,
        *,
        tenant_id: str,
        owner_user_id: str,
        arena_id: str,
        triggered_by: str,
    ) -> dict[str, Any]:
        """Запускает C5 run-заявку после guardrail проверки и пишет launch_history."""

        normalized_triggered_by = triggered_by.strip() or "manual"
        with self._lock:
            data = self._read_store()
            workspace = self._find_workspace(
                data=data,
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                workspace_id=arena_id,
            )
            optimizer_state = _normalize_optimizer_studio_state(workspace.get("optimizer_studio"))
            dataset_state = _normalize_dataset_studio_state(workspace.get("dataset_studio"))
            evaluation_state = _normalize_evaluation_studio_state(workspace.get("evaluation_studio"))
            candidate_set_draft = workspace.get("candidate_set_draft")
            issues = _build_optimizer_setup_issues(
                optimizer_state=optimizer_state,
                dataset_state=dataset_state,
                evaluation_state=evaluation_state,
                candidate_set_draft=candidate_set_draft if isinstance(candidate_set_draft, dict) else None,
            )
            if any(item.get("severity") == "error" for item in issues):
                raise ValueError("Optimizer launch blocked by guardrails.")

            enabled_methods = [item for item in optimizer_state.get("methods", []) if bool(item.get("enabled", False))]
            method_id = str(enabled_methods[0].get("method_id", "")) if enabled_methods else ""
            run_entry = {
                "run_id": f"run_{uuid4().hex[:10]}",
                "created_at": _utc_now_iso(),
                "status": "queued",
                "method_id": method_id,
                "epochs_total": int(optimizer_state.get("run_plan", {}).get("epochs_total", 0) or 0),
                "selected_candidates_total": _count_candidates_selected_for_tests(candidate_set_draft if isinstance(candidate_set_draft, dict) else None),
                "assigned_datasets_total": len(dataset_state.get("assigned_dataset_ids", [])),
                "triggered_by": normalized_triggered_by,
            }
            launch_history = optimizer_state.get("launch_history", [])
            launch_history.append(run_entry)
            optimizer_state["launch_history"] = launch_history[-20:]
            optimizer_state["updated_at"] = _utc_now_iso()
            workspace["optimizer_studio"] = optimizer_state
            self._write_store(data)
            return dict(run_entry)

    def _read_store(self) -> dict[str, Any]:
        """Читает JSON-store и гарантирует корректный базовый контракт."""

        try:
            raw = self._store_file.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (json.JSONDecodeError, OSError):
            payload = {"version": "workspace_registry_v1", "workspaces": []}
        if not isinstance(payload, dict):
            payload = {"version": "workspace_registry_v1", "workspaces": []}
        if "workspaces" not in payload or not isinstance(payload["workspaces"], list):
            payload["workspaces"] = []
        if "version" not in payload:
            payload["version"] = "workspace_registry_v1"
        return payload

    def _write_store(self, data: dict[str, Any]) -> None:
        """Записывает JSON-store атомарно через временный файл."""

        temp_file = self._store_file.with_suffix(f"{self._store_file.suffix}.tmp")
        temp_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_file.replace(self._store_file)

    def _workspace_to_record(self, workspace: dict[str, Any]) -> WorkspaceRecord:
        """Преобразует внутренний dict workspace в API-DTO."""

        return WorkspaceRecord(
            workspace_id=str(workspace["workspace_id"]),
            name=str(workspace["name"]),
            description=str(workspace.get("description", "")),
            created_at=str(workspace["created_at"]),
            tenant_id=str(workspace.get("tenant_id", "")),
            owner_user_id=str(workspace.get("owner_user_id", "")),
        )

    def _project_to_record(self, project: dict[str, Any]) -> ProjectRecord:
        """Преобразует внутренний dict project в API-DTO."""

        return ProjectRecord(
            project_id=str(project["project_id"]),
            workspace_id=str(project["workspace_id"]),
            name=str(project["name"]),
            description=str(project.get("description", "")),
            status=str(project.get("status", "draft")),
            created_at=str(project["created_at"]),
            updated_at=str(project["updated_at"]),
            tenant_id=str(project.get("tenant_id", "")),
            owner_user_id=str(project.get("owner_user_id", "")),
        )

    def _assert_unique_workspace_name(
        self,
        *,
        data: dict[str, Any],
        tenant_id: str,
        owner_user_id: str,
        name: str,
    ) -> None:
        """Проверяет уникальность workspace-имени в tenant/user scope."""

        for item in data.get("workspaces", []):
            if (
                str(item.get("tenant_id", "")) == tenant_id
                and str(item.get("owner_user_id", "")) == owner_user_id
                and str(item.get("name", "")).strip().lower() == name.strip().lower()
            ):
                raise ValueError("Workspace with the same name already exists.")

    def _find_workspace(
        self,
        *,
        data: dict[str, Any],
        tenant_id: str,
        owner_user_id: str,
        workspace_id: str,
    ) -> dict[str, Any]:
        """Ищет workspace по идентификатору и выбрасывает KeyError, если он не найден."""

        for item in data.get("workspaces", []):
            if (
                str(item.get("workspace_id")) == workspace_id
                and str(item.get("tenant_id", "")) == tenant_id
                and str(item.get("owner_user_id", "")) == owner_user_id
            ):
                return item
        raise KeyError(f"Workspace not found: {workspace_id}")

    def _find_project(
        self,
        *,
        data: dict[str, Any],
        tenant_id: str,
        owner_user_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """Ищет проект по id в tenant/user scope и возвращает mutable dict-объект."""

        for workspace in data.get("workspaces", []):
            projects = workspace.get("projects", [])
            if not isinstance(projects, list):
                continue
            for project in projects:
                if not isinstance(project, dict):
                    continue
                if (
                    str(project.get("project_id")) == project_id
                    and str(project.get("tenant_id", "")) == tenant_id
                    and str(project.get("owner_user_id", "")) == owner_user_id
                ):
                    return project
        raise KeyError(f"Project not found: {project_id}")


def _utc_now_iso() -> str:
    """Возвращает UTC timestamp в ISO-формате для audit-полей сущностей."""

    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()


def _make_unique_workspace_copy_name(*, source_name: str, existing_names: set[str]) -> str:
    """Строит уникальное имя копии workspace вида '<name> copy', '<name> copy 2', ..."""

    base_name = source_name.strip() or "workspace"
    candidate = f"{base_name} copy"
    if candidate.lower() not in existing_names:
        return candidate
    counter = 2
    while True:
        candidate = f"{base_name} copy {counter}"
        if candidate.lower() not in existing_names:
            return candidate
        counter += 1


def _build_message(*, role: str, content: str) -> dict[str, str]:
    """Валидирует и формирует chat-сообщение для arena/project чатов."""

    normalized_role = role.strip().lower()
    normalized_content = content.strip()
    if normalized_role not in {"user", "assistant", "system"}:
        raise ValueError("Chat message role must be one of: user, assistant, system.")
    if not normalized_content:
        raise ValueError("Chat message content must be a non-empty string.")
    return {
        "message_id": f"msg_{uuid4().hex[:10]}",
        "role": normalized_role,
        "content": normalized_content,
        "created_at": _utc_now_iso(),
    }


def _serialize_messages(raw_messages: Any) -> list[dict[str, Any]]:
    """Нормализует список сообщений в безопасный сериализуемый формат."""

    if not isinstance(raw_messages, list):
        return []
    return [_serialize_message(item) for item in raw_messages if isinstance(item, dict)]


def _serialize_message(raw_message: dict[str, Any]) -> dict[str, Any]:
    """Нормализует одиночное сообщение в контракт API ответа."""

    return {
        "message_id": str(raw_message.get("message_id", "")),
        "role": str(raw_message.get("role", "user")),
        "content": str(raw_message.get("content", "")),
        "created_at": str(raw_message.get("created_at", "")),
    }


def _build_default_pattern_selection() -> dict[str, Any]:
    """Строит default include/exclude выборку паттернов."""

    return {
        "include_pattern_ids": [],
        "exclude_pattern_ids": [],
        "updated_at": _utc_now_iso(),
    }


def _normalize_pattern_selection(raw_selection: Any) -> dict[str, Any]:
    """Нормализует pattern selection payload с валидацией пересечений include/exclude."""

    if not isinstance(raw_selection, dict):
        return _build_default_pattern_selection()

    include_raw = raw_selection.get("include_pattern_ids", [])
    exclude_raw = raw_selection.get("exclude_pattern_ids", [])
    updated_at_raw = raw_selection.get("updated_at", "")

    include_ids = _normalize_pattern_id_list(include_raw)
    exclude_ids = _normalize_pattern_id_list(exclude_raw)
    overlap = set(include_ids).intersection(exclude_ids)
    if overlap:
        raise ValueError("Pattern include/exclude lists must not overlap.")

    updated_at = str(updated_at_raw).strip() or _utc_now_iso()
    return {
        "include_pattern_ids": include_ids,
        "exclude_pattern_ids": exclude_ids,
        "updated_at": updated_at,
    }


def _normalize_pattern_id_list(raw_value: Any) -> list[str]:
    """Нормализует список pattern id в уникальный стабильный массив строк."""

    if not isinstance(raw_value, list):
        raise ValueError("Pattern id list must be an array.")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_value:
        if not isinstance(item, str):
            raise ValueError("Pattern id list must contain strings only.")
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _build_default_dataset_studio_state() -> dict[str, Any]:
    """Строит default-состояние Dataset Studio для новой арены."""

    return {
        "active_dataset_id": "",
        "assigned_dataset_ids": [],
        "datasets": [],
    }


def _normalize_dataset_studio_state(raw_state: Any) -> dict[str, Any]:
    """Нормализует состояние Dataset Studio и возвращает безопасный payload."""

    if not isinstance(raw_state, dict):
        return _build_default_dataset_studio_state()
    datasets_raw = raw_state.get("datasets", [])
    datasets: list[dict[str, Any]] = []
    if isinstance(datasets_raw, list):
        for item in datasets_raw:
            if not isinstance(item, dict):
                continue
            datasets.append(_normalize_dataset_payload(item))
    active_dataset_id = str(raw_state.get("active_dataset_id", "")).strip()
    if active_dataset_id and not any(str(item.get("dataset_id", "")) == active_dataset_id for item in datasets):
        active_dataset_id = ""
    if not active_dataset_id and datasets:
        active_dataset_id = str(datasets[0].get("dataset_id", ""))
    assigned_dataset_ids_raw = raw_state.get("assigned_dataset_ids", [])
    try:
        assigned_dataset_ids = _normalize_dataset_id_list(assigned_dataset_ids_raw)
    except ValueError:
        assigned_dataset_ids = []
    known_dataset_ids = {str(item.get("dataset_id", "")) for item in datasets}
    assigned_dataset_ids = [item for item in assigned_dataset_ids if item in known_dataset_ids]
    return {
        "active_dataset_id": active_dataset_id,
        "assigned_dataset_ids": assigned_dataset_ids,
        "datasets": datasets,
    }


def _normalize_dataset_payload(raw_dataset: dict[str, Any]) -> dict[str, Any]:
    """Нормализует один dataset с rows и version snapshots."""

    dataset_id = str(raw_dataset.get("dataset_id", "")).strip() or f"dset_{uuid4().hex[:10]}"
    name = str(raw_dataset.get("name", "")).strip() or "dataset"
    description = str(raw_dataset.get("description", "")).strip()
    created_at = str(raw_dataset.get("created_at", "")).strip() or _utc_now_iso()
    updated_at = str(raw_dataset.get("updated_at", "")).strip() or created_at
    rows_raw = raw_dataset.get("rows", [])
    versions_raw = raw_dataset.get("versions", [])
    rows = [_normalize_dataset_row(item) for item in rows_raw if isinstance(item, dict)] if isinstance(rows_raw, list) else []
    versions = [_normalize_dataset_version(item) for item in versions_raw if isinstance(item, dict)] if isinstance(versions_raw, list) else []
    return {
        "dataset_id": dataset_id,
        "name": name,
        "description": description,
        "created_at": created_at,
        "updated_at": updated_at,
        "rows": rows,
        "versions": versions,
    }


_DATASET_TARGET_STAGES: tuple[str, ...] = ("retrieval", "rerank", "synthesis", "final")


def _normalize_dataset_target_stage(raw_stage: Any) -> str:
    """Нормализует целевую стадию dataset-row и валидирует допустимые значения."""

    stage = str(raw_stage or "final").strip().lower() or "final"
    if stage not in _DATASET_TARGET_STAGES:
        raise ValueError(f"Unsupported target_stage: {stage}")
    return stage


def _normalize_string_list(raw_value: Any) -> list[str]:
    """Нормализует массив строк: trim, unique, stable order."""

    if not isinstance(raw_value, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_value:
        value = str(item).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _coerce_expected_payload(*, target_stage: str, raw_payload: Any, raw_expected: Any) -> dict[str, Any]:
    """Строит stage-aware expected payload с обратной совместимостью к полю expected."""

    payload: dict[str, Any] = {}
    if isinstance(raw_payload, dict):
        payload = dict(raw_payload)
    elif isinstance(raw_expected, dict):
        payload = dict(raw_expected)
    elif isinstance(raw_expected, str):
        expected_text = raw_expected.strip()
        if expected_text:
            try:
                parsed = json.loads(expected_text)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, dict):
                payload = dict(parsed)
            elif target_stage == "final":
                payload = {"answer": expected_text}
            else:
                payload = {"text": expected_text}

    if target_stage == "retrieval":
        payload["evidence_ids"] = _normalize_string_list(payload.get("evidence_ids", payload.get("expected_evidence_ids", [])))
        payload["must_include"] = _normalize_string_list(payload.get("must_include", []))
    elif target_stage == "rerank":
        payload["ranked_ids"] = _normalize_string_list(payload.get("ranked_ids", payload.get("expected_ranking", [])))
    elif target_stage == "synthesis":
        payload["must_include"] = _normalize_string_list(payload.get("must_include", []))
        payload["forbidden"] = _normalize_string_list(payload.get("forbidden", []))
    else:
        payload["answer"] = str(payload.get("answer", payload.get("final_answer", payload.get("text", "")))).strip()
    return payload


def _stringify_expected_payload(*, target_stage: str, expected_payload: dict[str, Any]) -> str:
    """Готовит человекочитаемое поле expected для UI-редактора и legacy DTO."""

    if target_stage == "final":
        return str(expected_payload.get("answer", "")).strip()
    return json.dumps(expected_payload, ensure_ascii=False, sort_keys=True)


def _normalize_dataset_row(raw_row: Any) -> dict[str, Any]:
    """Нормализует одну dataset-row в stage-aware контракт c совместимостью v1."""

    if not isinstance(raw_row, dict):
        raise ValueError("Dataset row must be an object.")
    case_id = str(raw_row.get("case_id", "")).strip() or f"case_{uuid4().hex[:8]}"
    input_text = str(raw_row.get("input", "")).strip()
    target_stage = _normalize_dataset_target_stage(raw_row.get("target_stage", "final"))
    expected_payload = _coerce_expected_payload(
        target_stage=target_stage,
        raw_payload=raw_row.get("expected_payload"),
        raw_expected=raw_row.get("expected", ""),
    )
    expected_text = _stringify_expected_payload(target_stage=target_stage, expected_payload=expected_payload)
    notes = str(raw_row.get("notes", "")).strip()
    return {
        "case_id": case_id,
        "input": input_text,
        "target_stage": target_stage,
        "expected_payload": expected_payload,
        "expected": expected_text,
        "notes": notes,
    }


def _normalize_dataset_version(raw_version: dict[str, Any]) -> dict[str, Any]:
    """Нормализует metadata version snapshot dataset."""

    version_id = str(raw_version.get("version_id", "")).strip() or f"dsv_{uuid4().hex[:10]}"
    label = str(raw_version.get("label", "")).strip() or version_id
    created_at = str(raw_version.get("created_at", "")).strip() or _utc_now_iso()
    source = str(raw_version.get("source", "")).strip() or "manual"
    rows_snapshot_raw = raw_version.get("rows_snapshot", [])
    rows_snapshot = (
        [_normalize_dataset_row(item) for item in rows_snapshot_raw if isinstance(item, dict)]
        if isinstance(rows_snapshot_raw, list)
        else []
    )
    rows_total_raw = raw_version.get("rows_total", len(rows_snapshot))
    try:
        rows_total = int(rows_total_raw)
    except (TypeError, ValueError):
        rows_total = len(rows_snapshot)
    return {
        "version_id": version_id,
        "label": label,
        "created_at": created_at,
        "rows_total": rows_total,
        "source": source,
        "rows_snapshot": rows_snapshot,
    }


def _find_dataset_by_id(*, studio_state: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    """Ищет dataset по id и бросает KeyError, если dataset отсутствует."""

    normalized_dataset_id = str(dataset_id).strip()
    datasets = studio_state.get("datasets", [])
    for dataset in datasets:
        if str(dataset.get("dataset_id", "")) == normalized_dataset_id:
            return dataset
    raise KeyError(f"Dataset not found: {normalized_dataset_id}")


def _normalize_dataset_id_list(raw_value: Any) -> list[str]:
    """Нормализует список dataset id в уникальный стабильный массив строк."""

    if not isinstance(raw_value, list):
        raise ValueError("Dataset id list must be an array.")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_value:
        if not isinstance(item, str):
            raise ValueError("Dataset id list must contain strings only.")
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


# Русский комментарий: требования к feature-флагам для comparative-метрик.
_COMPARATIVE_METRIC_REQUIRED_FEATURES: dict[str, tuple[str, ...]] = {
    "quality_f1": (),
    "cost_per_case": (),
    "latency_p95": (),
}

# Русский комментарий: требования к feature-флагам для diagnostic-сигналов.
_DIAGNOSTIC_SIGNAL_REQUIRED_FEATURES: dict[str, tuple[str, ...]] = {
    "retrieval_coverage": ("retrieval",),
    "rerank_gain": ("rerank",),
    "synthesis_drift": ("llm",),
}


def _build_default_evaluation_studio_state() -> dict[str, Any]:
    """Строит default-состояние C4 Metrics & Evaluators Studio для новой арены."""

    default_profile = _build_default_evaluation_profile(
        profile_id="ep_default",
        name="Default evaluation profile",
        description="Initial comparative/diagnostic configuration.",
    )
    now = _utc_now_iso()
    return {
        "active_profile_id": str(default_profile.get("profile_id", "")),
        "assigned_profile_ids": [str(default_profile.get("profile_id", ""))],
        "profiles": [default_profile],
        # Русский комментарий: зеркалим активный профиль в legacy-поля для обратной совместимости API.
        "comparative_metrics": [dict(item) for item in default_profile.get("comparative_metrics", [])],
        "diagnostic_signals": [dict(item) for item in default_profile.get("diagnostic_signals", [])],
        "evaluators": [dict(item) for item in default_profile.get("evaluators", [])],
        "evaluator_metric_links": [dict(item) for item in default_profile.get("evaluator_metric_links", [])],
        "budget": dict(default_profile.get("budget", {})),
        "versions": [dict(item) for item in default_profile.get("versions", [])],
        "updated_at": now,
    }


def _build_default_evaluation_profile(
    *,
    profile_id: str,
    name: str,
    description: str,
    comparative_metrics: list[dict[str, Any]] | None = None,
    diagnostic_signals: list[dict[str, Any]] | None = None,
    evaluators: list[dict[str, Any]] | None = None,
    budget: dict[str, Any] | None = None,
    versions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Строит default metrics-profile C4, который может использоваться и для миграции legacy-формата."""

    now = _utc_now_iso()
    base_comparative_metrics = comparative_metrics if comparative_metrics is not None else [
        {
            "metric_id": "quality_f1",
            "title": "Quality F1@K",
            "description": "Primary quality metric used for ranking.",
            "enabled": True,
            "weight": 0.6,
        },
        {
            "metric_id": "cost_per_case",
            "title": "Cost / case",
            "description": "Average spend per evaluated case.",
            "enabled": True,
            "weight": 0.2,
        },
        {
            "metric_id": "latency_p95",
            "title": "Latency P95",
            "description": "Tail latency quality guardrail.",
            "enabled": True,
            "weight": 0.2,
        },
    ]
    base_diagnostic_signals = diagnostic_signals if diagnostic_signals is not None else [
        {
            "signal_id": "retrieval_coverage",
            "title": "Retrieval coverage",
            "description": "Tracks whether retrieval stage found relevant evidence.",
            "enabled": True,
        },
        {
            "signal_id": "rerank_gain",
            "title": "Rerank gain",
            "description": "Shows ranking improvement over raw retrieval.",
            "enabled": True,
        },
        {
            "signal_id": "synthesis_drift",
            "title": "Synthesis drift",
            "description": "Measures answer drift from provided evidence.",
            "enabled": True,
        },
    ]
    base_evaluators = evaluators if evaluators is not None else [
        {
            "evaluator_id": "golden_oracle",
            "title": "Golden dataset oracle",
            "description": "Deterministic baseline evaluator on expected outputs.",
            "enabled": True,
        },
        {
            "evaluator_id": "llm_judge",
            "title": "LLM as a judge",
            "description": "Model-based semantic quality review.",
            "enabled": False,
        },
        {
            "evaluator_id": "executable_validator",
            "title": "Executable validator",
            "description": "External executable checks (tests/code/render).",
            "enabled": False,
        },
    ]
    normalized_comparative_metrics = _normalize_comparative_metrics(base_comparative_metrics)
    normalized_diagnostic_signals = _normalize_diagnostic_signals(base_diagnostic_signals)
    normalized_evaluators = _normalize_evaluators(base_evaluators)
    base_budget = budget if budget is not None else {"max_cases": 20, "max_llm_calls": 100, "max_cost_usd": 5.0}
    base_versions = versions if versions is not None else []
    return {
        "profile_id": str(profile_id).strip() or f"ep_{uuid4().hex[:10]}",
        "name": str(name).strip() or "Evaluation profile",
        "description": str(description).strip(),
        "comparative_metrics": normalized_comparative_metrics,
        "diagnostic_signals": normalized_diagnostic_signals,
        "evaluators": normalized_evaluators,
        "evaluator_metric_links": _normalize_evaluator_metric_links(
            raw_links=[],
            comparative_metrics=normalized_comparative_metrics,
            diagnostic_signals=normalized_diagnostic_signals,
            evaluators=normalized_evaluators,
        ),
        "budget": _normalize_evaluation_budget(base_budget),
        "versions": [_normalize_evaluation_version(item) for item in base_versions if isinstance(item, dict)],
        "created_at": now,
        "updated_at": now,
    }


def _normalize_evaluation_profile_payload(raw_profile: Any) -> dict[str, Any]:
    """Нормализует один metrics-profile C4 в стабильный контракт хранения."""

    if not isinstance(raw_profile, dict):
        raise ValueError("Evaluation profile must be an object.")
    profile_id = str(raw_profile.get("profile_id", "")).strip() or f"ep_{uuid4().hex[:10]}"
    name = str(raw_profile.get("name", "")).strip() or profile_id
    description = str(raw_profile.get("description", "")).strip()
    comparative_raw = raw_profile.get("comparative_metrics", [])
    diagnostic_raw = raw_profile.get("diagnostic_signals", [])
    evaluators_raw = raw_profile.get("evaluators", [])
    evaluator_metric_links_raw = raw_profile.get("evaluator_metric_links", [])
    budget_raw = raw_profile.get("budget", {})
    versions_raw = raw_profile.get("versions", [])
    created_at = str(raw_profile.get("created_at", "")).strip() or _utc_now_iso()
    updated_at = str(raw_profile.get("updated_at", "")).strip() or created_at
    versions: list[dict[str, Any]] = []
    if isinstance(versions_raw, list):
        for item in versions_raw:
            if isinstance(item, dict):
                versions.append(_normalize_evaluation_version(item))
    normalized_comparative_metrics = _normalize_comparative_metrics(comparative_raw)
    normalized_diagnostic_signals = _normalize_diagnostic_signals(diagnostic_raw)
    normalized_evaluators = _normalize_evaluators(evaluators_raw)
    return {
        "profile_id": profile_id,
        "name": name,
        "description": description,
        "comparative_metrics": normalized_comparative_metrics,
        "diagnostic_signals": normalized_diagnostic_signals,
        "evaluators": normalized_evaluators,
        "evaluator_metric_links": _normalize_evaluator_metric_links(
            raw_links=evaluator_metric_links_raw,
            comparative_metrics=normalized_comparative_metrics,
            diagnostic_signals=normalized_diagnostic_signals,
            evaluators=normalized_evaluators,
        ),
        "budget": _normalize_evaluation_budget(budget_raw),
        "versions": versions,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def _normalize_evaluation_studio_state(raw_state: Any) -> dict[str, Any]:
    """Нормализует состояние C4 Metrics & Evaluators Studio."""

    default_state = _build_default_evaluation_studio_state()
    if not isinstance(raw_state, dict):
        return default_state

    profiles: list[dict[str, Any]] = []
    profiles_raw = raw_state.get("profiles", [])
    if isinstance(profiles_raw, list):
        for item in profiles_raw:
            if not isinstance(item, dict):
                continue
            try:
                profiles.append(_normalize_evaluation_profile_payload(item))
            except ValueError:
                continue

    # Русский комментарий: миграция legacy-полей в единый profile-формат.
    if not profiles:
        try:
            legacy_profile = _build_default_evaluation_profile(
                profile_id="ep_default",
                name="Default evaluation profile",
                description="Migrated from legacy C4 evaluation state.",
                comparative_metrics=raw_state.get("comparative_metrics", default_state.get("comparative_metrics", [])),
                diagnostic_signals=raw_state.get("diagnostic_signals", default_state.get("diagnostic_signals", [])),
                evaluators=raw_state.get("evaluators", default_state.get("evaluators", [])),
                budget=raw_state.get("budget", default_state.get("budget", {})),
                versions=raw_state.get("versions", []),
            )
        except ValueError:
            legacy_profile = _build_default_evaluation_profile(
                profile_id="ep_default",
                name="Default evaluation profile",
                description="Recovered default profile.",
            )
        profiles = [legacy_profile]

    known_profile_ids = {str(item.get("profile_id", "")) for item in profiles}
    active_profile_id = str(raw_state.get("active_profile_id", "")).strip()
    if active_profile_id not in known_profile_ids:
        active_profile_id = str(profiles[0].get("profile_id", ""))
    assigned_profile_ids = _normalize_evaluation_profile_id_list(raw_state.get("assigned_profile_ids", []))
    assigned_profile_ids = [item for item in assigned_profile_ids if item in known_profile_ids]
    if not assigned_profile_ids:
        assigned_profile_ids = [active_profile_id]
    updated_at = str(raw_state.get("updated_at", "")).strip() or _utc_now_iso()
    active_profile = _find_evaluation_profile_by_id(
        studio_state={"profiles": profiles},
        profile_id=active_profile_id,
    )
    return {
        "active_profile_id": active_profile_id,
        "assigned_profile_ids": assigned_profile_ids,
        "profiles": profiles,
        # Русский комментарий: legacy mirror-поля для текущего UI/API контракта.
        "comparative_metrics": [dict(item) for item in active_profile.get("comparative_metrics", [])],
        "diagnostic_signals": [dict(item) for item in active_profile.get("diagnostic_signals", [])],
        "evaluators": [dict(item) for item in active_profile.get("evaluators", [])],
        "evaluator_metric_links": [dict(item) for item in active_profile.get("evaluator_metric_links", [])],
        "budget": dict(active_profile.get("budget", {})),
        "versions": [dict(item) for item in active_profile.get("versions", [])],
        "updated_at": updated_at,
    }


def _normalize_evaluation_profile_id_list(raw_value: Any) -> list[str]:
    """Нормализует список profile id в уникальный стабильный массив строк."""

    if not isinstance(raw_value, list):
        raise ValueError("Evaluation profile id list must be an array.")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_value:
        if not isinstance(item, str):
            raise ValueError("Evaluation profile id list must contain strings only.")
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _find_evaluation_profile_by_id(*, studio_state: dict[str, Any], profile_id: str) -> dict[str, Any]:
    """Ищет metrics-profile по id и выбрасывает KeyError, если он отсутствует."""

    normalized_profile_id = str(profile_id).strip()
    profiles = studio_state.get("profiles", [])
    for profile in profiles:
        if str(profile.get("profile_id", "")) == normalized_profile_id:
            return profile
    raise KeyError(f"Evaluation profile not found: {normalized_profile_id}")


def _find_target_evaluation_profile(*, studio_state: dict[str, Any], profile_id: str | None) -> dict[str, Any]:
    """Возвращает target metrics-profile по profile_id или по active_profile_id."""

    if profile_id is not None and str(profile_id).strip():
        return _find_evaluation_profile_by_id(studio_state=studio_state, profile_id=str(profile_id))
    active_profile_id = str(studio_state.get("active_profile_id", "")).strip()
    if active_profile_id:
        return _find_evaluation_profile_by_id(studio_state=studio_state, profile_id=active_profile_id)
    profiles = studio_state.get("profiles", [])
    if not profiles:
        raise KeyError("Evaluation profile not found: active_profile_id is empty.")
    return profiles[0]


def _sync_evaluation_studio_legacy_mirror_fields(studio_state: dict[str, Any]) -> None:
    """Синхронизирует legacy-поля C4 с активным профилем для обратной совместимости API-контрактов."""

    active_profile = _find_target_evaluation_profile(studio_state=studio_state, profile_id=None)
    studio_state["comparative_metrics"] = [dict(item) for item in active_profile.get("comparative_metrics", [])]
    studio_state["diagnostic_signals"] = [dict(item) for item in active_profile.get("diagnostic_signals", [])]
    studio_state["evaluators"] = [dict(item) for item in active_profile.get("evaluators", [])]
    studio_state["evaluator_metric_links"] = [dict(item) for item in active_profile.get("evaluator_metric_links", [])]
    studio_state["budget"] = dict(active_profile.get("budget", {}))
    studio_state["versions"] = [dict(item) for item in active_profile.get("versions", [])]


def _normalize_required_features(*, raw_required_features: Any) -> list[str]:
    """Нормализует required-features метрики/сигнала в уникальный список строк."""

    if not isinstance(raw_required_features, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_required_features:
        if not isinstance(item, str):
            continue
        value = item.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _normalize_comparative_metrics(raw_metrics: Any) -> list[dict[str, Any]]:
    """Нормализует список comparative метрик в стабильный формат."""

    if not isinstance(raw_metrics, list):
        raise ValueError("Comparative metrics must be an array.")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_metrics:
        if not isinstance(item, dict):
            raise ValueError("Comparative metrics must contain objects only.")
        metric_id = str(item.get("metric_id", "")).strip()
        if not metric_id or metric_id in seen:
            continue
        seen.add(metric_id)
        try:
            weight = float(item.get("weight", 0.0) or 0.0)
        except (TypeError, ValueError):
            weight = 0.0
        required_features = _normalize_required_features(raw_required_features=item.get("required_features", []))
        availability_status = "available" if str(item.get("availability_status", "available")).strip() != "unavailable" else "unavailable"
        availability_reason = str(item.get("availability_reason", "")).strip()
        normalized.append(
            {
                "metric_id": metric_id,
                "title": str(item.get("title", metric_id)).strip() or metric_id,
                "description": str(item.get("description", "")).strip(),
                "enabled": bool(item.get("enabled", False)),
                "weight": round(weight, 6),
                "required_features": required_features,
                "availability_status": availability_status,
                "availability_reason": availability_reason,
            }
        )
    if not normalized:
        raise ValueError("Comparative metrics list must contain at least one metric.")
    return normalized


def _normalize_diagnostic_signals(raw_signals: Any) -> list[dict[str, Any]]:
    """Нормализует список diagnostic сигналов в стабильный формат."""

    if not isinstance(raw_signals, list):
        raise ValueError("Diagnostic signals must be an array.")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_signals:
        if not isinstance(item, dict):
            raise ValueError("Diagnostic signals must contain objects only.")
        signal_id = str(item.get("signal_id", "")).strip()
        if not signal_id or signal_id in seen:
            continue
        seen.add(signal_id)
        required_features = _normalize_required_features(raw_required_features=item.get("required_features", []))
        availability_status = "available" if str(item.get("availability_status", "available")).strip() != "unavailable" else "unavailable"
        availability_reason = str(item.get("availability_reason", "")).strip()
        normalized.append(
            {
                "signal_id": signal_id,
                "title": str(item.get("title", signal_id)).strip() or signal_id,
                "description": str(item.get("description", "")).strip(),
                "enabled": bool(item.get("enabled", False)),
                "required_features": required_features,
                "availability_status": availability_status,
                "availability_reason": availability_reason,
            }
        )
    if not normalized:
        raise ValueError("Diagnostic signals list must contain at least one signal.")
    return normalized


def _normalize_evaluators(raw_evaluators: Any) -> list[dict[str, Any]]:
    """Нормализует список evaluator-адаптеров в стабильный формат."""

    if not isinstance(raw_evaluators, list):
        raise ValueError("Evaluators must be an array.")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_evaluators:
        if not isinstance(item, dict):
            raise ValueError("Evaluators must contain objects only.")
        evaluator_id = str(item.get("evaluator_id", "")).strip()
        if not evaluator_id or evaluator_id in seen:
            continue
        seen.add(evaluator_id)
        normalized.append(
            {
                "evaluator_id": evaluator_id,
                "title": str(item.get("title", evaluator_id)).strip() or evaluator_id,
                "description": str(item.get("description", "")).strip(),
                "enabled": bool(item.get("enabled", False)),
            }
        )
    if not normalized:
        raise ValueError("Evaluators list must contain at least one evaluator.")
    return normalized


def _normalize_evaluator_metric_links(
    *,
    raw_links: Any,
    comparative_metrics: list[dict[str, Any]],
    diagnostic_signals: list[dict[str, Any]],
    evaluators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Нормализует матрицу связей evaluator x metric и достраивает отсутствующие ячейки."""

    metric_refs = _build_metric_refs(
        comparative_metrics=comparative_metrics,
        diagnostic_signals=diagnostic_signals,
    )
    evaluator_ids = {str(item.get("evaluator_id", "")).strip() for item in evaluators}
    evaluator_ids = {item for item in evaluator_ids if item}
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    links_list = raw_links if isinstance(raw_links, list) else []
    for item in links_list:
        if not isinstance(item, dict):
            continue
        evaluator_id = str(item.get("evaluator_id", "")).strip()
        metric_kind = str(item.get("metric_kind", "")).strip().lower()
        metric_id = str(item.get("metric_id", "")).strip()
        link_key = (metric_kind, metric_id)
        if evaluator_id not in evaluator_ids or link_key not in metric_refs:
            continue
        dedupe_key = (evaluator_id, metric_kind, metric_id)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(
            {
                "evaluator_id": evaluator_id,
                "metric_kind": metric_kind,
                "metric_id": metric_id,
                "enabled": bool(item.get("enabled", False)),
            }
        )

    # Русский комментарий: автоматически достраиваем отсутствующие связи, чтобы матрица всегда была полной.
    evaluator_enabled_map = {
        str(item.get("evaluator_id", "")).strip(): bool(item.get("enabled", False))
        for item in evaluators
        if isinstance(item, dict)
    }
    for evaluator_id in sorted(evaluator_ids):
        for metric_kind, metric_id in sorted(metric_refs.keys()):
            dedupe_key = (evaluator_id, metric_kind, metric_id)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            normalized.append(
                {
                    "evaluator_id": evaluator_id,
                    "metric_kind": metric_kind,
                    "metric_id": metric_id,
                    "enabled": bool(evaluator_enabled_map.get(evaluator_id, False)),
                }
            )
    return normalized


def _build_metric_refs(
    *,
    comparative_metrics: list[dict[str, Any]],
    diagnostic_signals: list[dict[str, Any]],
) -> dict[tuple[str, str], str]:
    """Строит индекс метрик/сигналов для матрицы покрытий evaluator x metric."""

    metric_refs: dict[tuple[str, str], str] = {}
    for item in comparative_metrics:
        if not isinstance(item, dict):
            continue
        metric_id = str(item.get("metric_id", "")).strip()
        if not metric_id:
            continue
        metric_refs[("comparative", metric_id)] = str(item.get("title", metric_id)).strip() or metric_id
    for item in diagnostic_signals:
        if not isinstance(item, dict):
            continue
        signal_id = str(item.get("signal_id", "")).strip()
        if not signal_id:
            continue
        metric_refs[("diagnostic", signal_id)] = str(item.get("title", signal_id)).strip() or signal_id
    return metric_refs


def _normalize_evaluation_budget(raw_budget: Any) -> dict[str, Any]:
    """Нормализует бюджет evaluation profile."""

    if not isinstance(raw_budget, dict):
        raise ValueError("Budget must be an object.")
    try:
        max_cases = int(raw_budget.get("max_cases", 0) or 0)
    except (TypeError, ValueError):
        max_cases = 0
    try:
        max_llm_calls = int(raw_budget.get("max_llm_calls", 0) or 0)
    except (TypeError, ValueError):
        max_llm_calls = 0
    try:
        max_cost_usd = float(raw_budget.get("max_cost_usd", 0.0) or 0.0)
    except (TypeError, ValueError):
        max_cost_usd = 0.0
    return {
        "max_cases": max_cases,
        "max_llm_calls": max_llm_calls,
        "max_cost_usd": round(max_cost_usd, 6),
    }


def _normalize_evaluation_version(raw_version: dict[str, Any]) -> dict[str, Any]:
    """Нормализует snapshot-версию evaluation profile."""

    version_id = str(raw_version.get("version_id", "")).strip() or f"evv_{uuid4().hex[:10]}"
    label = str(raw_version.get("label", "")).strip() or version_id
    created_at = str(raw_version.get("created_at", "")).strip() or _utc_now_iso()
    source = str(raw_version.get("source", "")).strip() or "manual"
    comparative_metrics_raw = raw_version.get("comparative_metrics", [])
    diagnostic_signals_raw = raw_version.get("diagnostic_signals", [])
    evaluators_raw = raw_version.get("evaluators", [])
    evaluator_metric_links_raw = raw_version.get("evaluator_metric_links", [])
    budget_raw = raw_version.get("budget", {})
    normalized_comparative_metrics = _normalize_comparative_metrics(comparative_metrics_raw)
    normalized_diagnostic_signals = _normalize_diagnostic_signals(diagnostic_signals_raw)
    normalized_evaluators = _normalize_evaluators(evaluators_raw)
    return {
        "version_id": version_id,
        "label": label,
        "created_at": created_at,
        "source": source,
        "comparative_metrics": normalized_comparative_metrics,
        "diagnostic_signals": normalized_diagnostic_signals,
        "evaluators": normalized_evaluators,
        "evaluator_metric_links": _normalize_evaluator_metric_links(
            raw_links=evaluator_metric_links_raw,
            comparative_metrics=normalized_comparative_metrics,
            diagnostic_signals=normalized_diagnostic_signals,
            evaluators=normalized_evaluators,
        ),
        "budget": _normalize_evaluation_budget(budget_raw),
    }


def _build_evaluation_profile_validation_report(*, profile: dict[str, Any]) -> dict[str, Any]:
    """Строит валидированный отчет C4 evaluation profile без повторного чтения store."""

    comparative_metrics = profile.get("comparative_metrics", [])
    diagnostic_signals = profile.get("diagnostic_signals", [])
    evaluators = profile.get("evaluators", [])
    evaluator_metric_links = profile.get("evaluator_metric_links", [])
    budget = profile.get("budget", {})
    issues: list[dict[str, Any]] = []

    enabled_comparative_metrics = [
        item
        for item in comparative_metrics
        if bool(item.get("enabled", False)) and str(item.get("availability_status", "available")) != "unavailable"
    ]
    if not enabled_comparative_metrics:
        issues.append(
            {
                "severity": "error",
                "code": "missing_comparative_metric",
                "message": "At least one comparative metric must be enabled.",
            }
        )
    weight_sum = sum(float(item.get("weight", 0.0) or 0.0) for item in enabled_comparative_metrics)
    if enabled_comparative_metrics and weight_sum <= 0:
        issues.append(
            {
                "severity": "error",
                "code": "invalid_metric_weights",
                "message": "Comparative metric weights must have a positive total.",
            }
        )
    if not any(
        bool(item.get("enabled", False)) and str(item.get("availability_status", "available")) != "unavailable"
        for item in diagnostic_signals
    ):
        issues.append(
            {
                "severity": "warning",
                "code": "missing_diagnostic_signal",
                "message": "No diagnostic signal is enabled.",
            }
        )
    if not any(bool(item.get("enabled", False)) for item in evaluators):
        issues.append(
            {
                "severity": "error",
                "code": "missing_evaluator",
                "message": "At least one evaluator must be enabled.",
            }
        )
    else:
        enabled_evaluator_ids = {
            str(item.get("evaluator_id", "")).strip()
            for item in evaluators
            if isinstance(item, dict) and bool(item.get("enabled", False))
        }
        link_coverage = {
            (
                str(item.get("metric_kind", "")).strip().lower(),
                str(item.get("metric_id", "")).strip(),
            )
            for item in evaluator_metric_links
            if isinstance(item, dict)
            and bool(item.get("enabled", False))
            and str(item.get("evaluator_id", "")).strip() in enabled_evaluator_ids
        }
        enabled_metric_refs: list[tuple[str, str, str]] = []
        for item in comparative_metrics:
            if not isinstance(item, dict):
                continue
            if not bool(item.get("enabled", False)) or str(item.get("availability_status", "available")) == "unavailable":
                continue
            metric_id = str(item.get("metric_id", "")).strip()
            if metric_id:
                enabled_metric_refs.append(("comparative", metric_id, str(item.get("title", metric_id)).strip() or metric_id))
        for item in diagnostic_signals:
            if not isinstance(item, dict):
                continue
            if not bool(item.get("enabled", False)) or str(item.get("availability_status", "available")) == "unavailable":
                continue
            signal_id = str(item.get("signal_id", "")).strip()
            if signal_id:
                enabled_metric_refs.append(("diagnostic", signal_id, str(item.get("title", signal_id)).strip() or signal_id))

        uncovered_metrics = [f"{title} ({kind}:{metric_id})" for kind, metric_id, title in enabled_metric_refs if (kind, metric_id) not in link_coverage]
        if uncovered_metrics:
            preview = ", ".join(uncovered_metrics[:5])
            suffix = "" if len(uncovered_metrics) <= 5 else f", +{len(uncovered_metrics) - 5} more"
            issues.append(
                {
                    "severity": "error",
                    "code": "evaluator_metric_coverage_gap",
                    "message": f"Missing evaluator links for enabled metrics/signals: {preview}{suffix}.",
                }
            )

    max_cases = int(budget.get("max_cases", 0) or 0)
    max_llm_calls = int(budget.get("max_llm_calls", 0) or 0)
    max_cost_usd = float(budget.get("max_cost_usd", 0.0) or 0.0)
    if max_cases <= 0:
        issues.append({"severity": "error", "code": "invalid_budget_cases", "message": "Budget `max_cases` must be greater than 0."})
    if max_llm_calls <= 0:
        issues.append({"severity": "warning", "code": "invalid_budget_llm_calls", "message": "Budget `max_llm_calls` should be greater than 0."})
    if max_cost_usd <= 0:
        issues.append({"severity": "warning", "code": "invalid_budget_cost", "message": "Budget `max_cost_usd` should be greater than 0."})

    status = "ready"
    if any(item.get("severity") == "error" for item in issues):
        status = "invalid"
    elif issues:
        status = "warnings"
    return {
        "status": status,
        "issues": issues,
        "updated_at": str(profile.get("updated_at", "")),
    }


def _build_default_optimizer_studio_state() -> dict[str, Any]:
    """Строит default-состояние C5 Optimizer Setup Studio для новой арены."""

    now = _utc_now_iso()
    return {
        "methods": [
            {
                "method_id": "random_search",
                "title": "Random search",
                "description": "Быстрый baseline по случайному обходу параметров.",
                "enabled": True,
            },
            {
                "method_id": "grid_search",
                "title": "Grid search",
                "description": "Детерминированный перебор фиксированных конфигураций.",
                "enabled": False,
            },
            {
                "method_id": "optuna_tpe",
                "title": "Optuna TPE",
                "description": "Байесовская стратегия для более глубокого поиска.",
                "enabled": False,
            },
        ],
        "controls": [
            {
                "control_id": "tune_prompts",
                "title": "Tune prompts",
                "description": "Разрешает эволюцию prompt-слоя кандидатов.",
                "enabled": True,
            },
            {
                "control_id": "tune_pattern_mix",
                "title": "Tune pattern mix",
                "description": "Разрешает менять комбинации pattern-blocks.",
                "enabled": True,
            },
            {
                "control_id": "allow_new_nodes",
                "title": "Allow new nodes",
                "description": "Разрешает добавлять новые node-компоненты.",
                "enabled": False,
            },
            {
                "control_id": "freeze_tools",
                "title": "Freeze tools",
                "description": "Фиксирует tool-слой, чтобы не ломать контракт.",
                "enabled": True,
            },
        ],
        "run_plan": {
            "epochs_total": 3,
            "candidates_per_epoch": 4,
            "max_parallel_trials": 2,
            "early_stop_patience": 1,
        },
        "budget": {
            "max_cases": 24,
            "max_llm_calls": 200,
            "max_cost_usd": 8.0,
            "max_runtime_minutes": 30,
        },
        "versions": [],
        "launch_history": [],
        "updated_at": now,
    }


def _normalize_optimizer_studio_state(raw_state: Any) -> dict[str, Any]:
    """Нормализует состояние C5 Optimizer Setup Studio."""

    default_state = _build_default_optimizer_studio_state()
    if not isinstance(raw_state, dict):
        return default_state
    methods_raw = raw_state.get("methods", default_state.get("methods", []))
    controls_raw = raw_state.get("controls", default_state.get("controls", []))
    run_plan_raw = raw_state.get("run_plan", default_state.get("run_plan", {}))
    budget_raw = raw_state.get("budget", default_state.get("budget", {}))
    versions_raw = raw_state.get("versions", [])
    launch_history_raw = raw_state.get("launch_history", [])
    updated_at = str(raw_state.get("updated_at", "")).strip() or _utc_now_iso()

    versions: list[dict[str, Any]] = []
    if isinstance(versions_raw, list):
        for item in versions_raw:
            if isinstance(item, dict):
                versions.append(_normalize_optimizer_version(item))

    launch_history: list[dict[str, Any]] = []
    if isinstance(launch_history_raw, list):
        for item in launch_history_raw:
            if not isinstance(item, dict):
                continue
            launch_history.append(
                {
                    "run_id": str(item.get("run_id", "")).strip() or f"run_{uuid4().hex[:10]}",
                    "created_at": str(item.get("created_at", "")).strip() or _utc_now_iso(),
                    "status": str(item.get("status", "queued")).strip() or "queued",
                    "method_id": str(item.get("method_id", "")).strip(),
                    "epochs_total": int(item.get("epochs_total", 0) or 0),
                    "selected_candidates_total": int(item.get("selected_candidates_total", 0) or 0),
                    "assigned_datasets_total": int(item.get("assigned_datasets_total", 0) or 0),
                    "triggered_by": str(item.get("triggered_by", "manual")).strip() or "manual",
                }
            )

    return {
        "methods": _normalize_optimizer_methods(methods_raw),
        "controls": _normalize_optimizer_controls(controls_raw),
        "run_plan": _normalize_optimizer_run_plan(run_plan_raw),
        "budget": _normalize_optimizer_budget(budget_raw),
        "versions": versions,
        "launch_history": launch_history[-20:],
        "updated_at": updated_at,
    }


def _normalize_optimizer_methods(raw_methods: Any) -> list[dict[str, Any]]:
    """Нормализует список optimizer methods."""

    if not isinstance(raw_methods, list):
        raise ValueError("Optimizer methods must be an array.")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_methods:
        if not isinstance(item, dict):
            raise ValueError("Optimizer methods must contain objects only.")
        method_id = str(item.get("method_id", "")).strip()
        if not method_id or method_id in seen:
            continue
        seen.add(method_id)
        normalized.append(
            {
                "method_id": method_id,
                "title": str(item.get("title", method_id)).strip() or method_id,
                "description": str(item.get("description", "")).strip(),
                "enabled": bool(item.get("enabled", False)),
            }
        )
    if not normalized:
        raise ValueError("Optimizer methods list must contain at least one method.")
    return normalized


def _normalize_optimizer_controls(raw_controls: Any) -> list[dict[str, Any]]:
    """Нормализует список optimizer controls."""

    if not isinstance(raw_controls, list):
        raise ValueError("Optimizer controls must be an array.")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_controls:
        if not isinstance(item, dict):
            raise ValueError("Optimizer controls must contain objects only.")
        control_id = str(item.get("control_id", "")).strip()
        if not control_id or control_id in seen:
            continue
        seen.add(control_id)
        normalized.append(
            {
                "control_id": control_id,
                "title": str(item.get("title", control_id)).strip() or control_id,
                "description": str(item.get("description", "")).strip(),
                "enabled": bool(item.get("enabled", False)),
            }
        )
    if not normalized:
        raise ValueError("Optimizer controls list must contain at least one control.")
    return normalized


def _normalize_optimizer_run_plan(raw_run_plan: Any) -> dict[str, Any]:
    """Нормализует блок run-plan C5 optimizer setup."""

    if not isinstance(raw_run_plan, dict):
        raise ValueError("Optimizer run_plan must be an object.")
    try:
        epochs_total = int(raw_run_plan.get("epochs_total", 0) or 0)
    except (TypeError, ValueError):
        epochs_total = 0
    try:
        candidates_per_epoch = int(raw_run_plan.get("candidates_per_epoch", 0) or 0)
    except (TypeError, ValueError):
        candidates_per_epoch = 0
    try:
        max_parallel_trials = int(raw_run_plan.get("max_parallel_trials", 0) or 0)
    except (TypeError, ValueError):
        max_parallel_trials = 0
    try:
        early_stop_patience = int(raw_run_plan.get("early_stop_patience", 0) or 0)
    except (TypeError, ValueError):
        early_stop_patience = 0
    return {
        "epochs_total": epochs_total,
        "candidates_per_epoch": candidates_per_epoch,
        "max_parallel_trials": max_parallel_trials,
        "early_stop_patience": early_stop_patience,
    }


def _normalize_optimizer_budget(raw_budget: Any) -> dict[str, Any]:
    """Нормализует бюджетные ограничения C5 optimizer setup."""

    if not isinstance(raw_budget, dict):
        raise ValueError("Optimizer budget must be an object.")
    try:
        max_cases = int(raw_budget.get("max_cases", 0) or 0)
    except (TypeError, ValueError):
        max_cases = 0
    try:
        max_llm_calls = int(raw_budget.get("max_llm_calls", 0) or 0)
    except (TypeError, ValueError):
        max_llm_calls = 0
    try:
        max_cost_usd = float(raw_budget.get("max_cost_usd", 0.0) or 0.0)
    except (TypeError, ValueError):
        max_cost_usd = 0.0
    try:
        max_runtime_minutes = int(raw_budget.get("max_runtime_minutes", 0) or 0)
    except (TypeError, ValueError):
        max_runtime_minutes = 0
    return {
        "max_cases": max_cases,
        "max_llm_calls": max_llm_calls,
        "max_cost_usd": round(max_cost_usd, 6),
        "max_runtime_minutes": max_runtime_minutes,
    }


def _normalize_optimizer_version(raw_version: dict[str, Any]) -> dict[str, Any]:
    """Нормализует snapshot-версию C5 optimizer setup."""

    version_id = str(raw_version.get("version_id", "")).strip() or f"opv_{uuid4().hex[:10]}"
    label = str(raw_version.get("label", "")).strip() or version_id
    created_at = str(raw_version.get("created_at", "")).strip() or _utc_now_iso()
    source = str(raw_version.get("source", "")).strip() or "manual"
    methods_raw = raw_version.get("methods", [])
    controls_raw = raw_version.get("controls", [])
    run_plan_raw = raw_version.get("run_plan", {})
    budget_raw = raw_version.get("budget", {})
    return {
        "version_id": version_id,
        "label": label,
        "created_at": created_at,
        "source": source,
        "methods": _normalize_optimizer_methods(methods_raw),
        "controls": _normalize_optimizer_controls(controls_raw),
        "run_plan": _normalize_optimizer_run_plan(run_plan_raw),
        "budget": _normalize_optimizer_budget(budget_raw),
    }


def _sync_evaluation_profile_availability(
    *,
    studio_state: dict[str, Any],
    candidate_set_draft: dict[str, Any] | None,
    profile_id: str | None = None,
) -> None:
    """Проставляет availability-статусы метрик/сигналов по feature-профилю выбранных кандидатов."""

    feature_flags = _extract_candidate_feature_flags(candidate_set_draft)
    target_profile = _find_target_evaluation_profile(studio_state=studio_state, profile_id=profile_id)
    target_profile["comparative_metrics"] = _apply_comparative_metric_availability(
        comparative_metrics=target_profile.get("comparative_metrics", []),
        feature_flags=feature_flags,
    )
    target_profile["diagnostic_signals"] = _apply_diagnostic_signal_availability(
        diagnostic_signals=target_profile.get("diagnostic_signals", []),
        feature_flags=feature_flags,
    )
    target_profile["evaluator_metric_links"] = _normalize_evaluator_metric_links(
        raw_links=target_profile.get("evaluator_metric_links", []),
        comparative_metrics=target_profile.get("comparative_metrics", []),
        diagnostic_signals=target_profile.get("diagnostic_signals", []),
        evaluators=target_profile.get("evaluators", []),
    )
    _sync_evaluation_studio_legacy_mirror_fields(studio_state)
    studio_state["candidate_features"] = dict(feature_flags)


def _apply_comparative_metric_availability(
    *,
    comparative_metrics: Any,
    feature_flags: dict[str, bool],
) -> list[dict[str, Any]]:
    """Возвращает comparative-метрики с вычисленным availability и безопасным enabled-флагом."""

    if not isinstance(comparative_metrics, list):
        return []
    normalized_metrics: list[dict[str, Any]] = []
    for item in comparative_metrics:
        if not isinstance(item, dict):
            continue
        normalized_item = dict(item)
        metric_id = str(normalized_item.get("metric_id", "")).strip()
        required_features = _normalize_required_features(raw_required_features=normalized_item.get("required_features", []))
        if not required_features:
            required_features = list(_COMPARATIVE_METRIC_REQUIRED_FEATURES.get(metric_id, ()))
        availability = _resolve_feature_availability(
            required_features=required_features,
            feature_flags=feature_flags,
        )
        normalized_item["required_features"] = required_features
        normalized_item["availability_status"] = "available" if availability["available"] else "unavailable"
        normalized_item["availability_reason"] = availability["reason"]
        if not availability["available"]:
            normalized_item["enabled"] = False
        normalized_metrics.append(normalized_item)
    return normalized_metrics


def _apply_diagnostic_signal_availability(
    *,
    diagnostic_signals: Any,
    feature_flags: dict[str, bool],
) -> list[dict[str, Any]]:
    """Возвращает diagnostic-сигналы с вычисленным availability и безопасным enabled-флагом."""

    if not isinstance(diagnostic_signals, list):
        return []
    normalized_signals: list[dict[str, Any]] = []
    for item in diagnostic_signals:
        if not isinstance(item, dict):
            continue
        normalized_item = dict(item)
        signal_id = str(normalized_item.get("signal_id", "")).strip()
        required_features = _normalize_required_features(raw_required_features=normalized_item.get("required_features", []))
        if not required_features:
            required_features = list(_DIAGNOSTIC_SIGNAL_REQUIRED_FEATURES.get(signal_id, ()))
        availability = _resolve_feature_availability(
            required_features=required_features,
            feature_flags=feature_flags,
        )
        normalized_item["required_features"] = required_features
        normalized_item["availability_status"] = "available" if availability["available"] else "unavailable"
        normalized_item["availability_reason"] = availability["reason"]
        if not availability["available"]:
            normalized_item["enabled"] = False
        normalized_signals.append(normalized_item)
    return normalized_signals


def _resolve_feature_availability(
    *,
    required_features: list[str],
    feature_flags: dict[str, bool],
) -> dict[str, Any]:
    """Сводит required-features в availability verdict с человекочитаемой причиной."""

    if not required_features:
        return {"available": True, "reason": "Available for all candidate structures."}
    missing_features = [feature for feature in required_features if not bool(feature_flags.get(feature, False))]
    if not missing_features:
        return {"available": True, "reason": f"Required features present: {', '.join(required_features)}."}
    return {"available": False, "reason": f"Requires features not found in selected candidates: {', '.join(missing_features)}."}


def _extract_candidate_feature_flags(candidate_set_draft: dict[str, Any] | None) -> dict[str, bool]:
    """Строит feature-флаги арены по mini-graph выбранных кандидатов."""

    flags: dict[str, bool] = {
        "core": False,
        "llm": False,
        "retrieval": False,
        "rerank": False,
        "tool": False,
        "hitl": False,
    }
    candidates = _resolve_candidates_for_feature_scan(candidate_set_draft)
    if not candidates:
        return flags
    flags["core"] = True
    for candidate in candidates:
        mini_graph = candidate.get("mini_graph", {})
        nodes = mini_graph.get("nodes", []) if isinstance(mini_graph, dict) else []
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_kind = str(node.get("kind", "")).strip().lower()
            node_label = str(node.get("label", "")).strip().lower()
            tokens = f"{node_kind} {node_label}"
            if "llm" in tokens:
                flags["llm"] = True
            if "retriev" in tokens or "rag" in tokens:
                flags["retrieval"] = True
            if "rerank" in tokens:
                flags["rerank"] = True
            if "tool" in tokens:
                flags["tool"] = True
            if "hitl" in tokens:
                flags["hitl"] = True
    return flags


def _resolve_candidates_for_feature_scan(candidate_set_draft: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Возвращает candidates для feature-анализа: selected_for_tests, иначе все candidates."""

    if not isinstance(candidate_set_draft, dict):
        return []
    candidates = candidate_set_draft.get("candidates", [])
    if not isinstance(candidates, list):
        return []
    candidate_objects = [item for item in candidates if isinstance(item, dict)]
    selected_candidates = [item for item in candidate_objects if bool(item.get("selected_for_tests", False))]
    if selected_candidates:
        return selected_candidates
    return candidate_objects


def _build_optimizer_setup_issues(
    *,
    optimizer_state: dict[str, Any],
    dataset_state: dict[str, Any],
    evaluation_state: dict[str, Any],
    candidate_set_draft: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Строит список guardrail-issues для preflight запуска optimizer."""

    issues: list[dict[str, Any]] = []
    methods = optimizer_state.get("methods", [])
    run_plan = optimizer_state.get("run_plan", {})
    budget = optimizer_state.get("budget", {})
    assigned_dataset_ids = dataset_state.get("assigned_dataset_ids", [])
    selected_candidates_total = _count_candidates_selected_for_tests(candidate_set_draft)
    compile_gate_status = _extract_candidate_compile_gate_status(candidate_set_draft)

    if not any(bool(item.get("enabled", False)) for item in methods):
        issues.append({"severity": "error", "code": "missing_optimizer_method", "message": "Enable at least one optimizer method."})
    if int(run_plan.get("epochs_total", 0) or 0) <= 0:
        issues.append({"severity": "error", "code": "invalid_epochs_total", "message": "Run plan `epochs_total` must be greater than 0."})
    if int(run_plan.get("candidates_per_epoch", 0) or 0) <= 0:
        issues.append(
            {"severity": "error", "code": "invalid_candidates_per_epoch", "message": "Run plan `candidates_per_epoch` must be greater than 0."}
        )
    if int(run_plan.get("max_parallel_trials", 0) or 0) <= 0:
        issues.append({"severity": "warning", "code": "invalid_parallel_trials", "message": "Run plan `max_parallel_trials` should be greater than 0."})

    if int(budget.get("max_cases", 0) or 0) <= 0:
        issues.append({"severity": "error", "code": "invalid_optimizer_budget_cases", "message": "Budget `max_cases` must be greater than 0."})
    if int(budget.get("max_llm_calls", 0) or 0) <= 0:
        issues.append({"severity": "warning", "code": "invalid_optimizer_budget_llm_calls", "message": "Budget `max_llm_calls` should be greater than 0."})
    if float(budget.get("max_cost_usd", 0.0) or 0.0) <= 0:
        issues.append({"severity": "warning", "code": "invalid_optimizer_budget_cost", "message": "Budget `max_cost_usd` should be greater than 0."})
    if int(budget.get("max_runtime_minutes", 0) or 0) <= 0:
        issues.append({"severity": "warning", "code": "invalid_optimizer_budget_runtime", "message": "Budget `max_runtime_minutes` should be greater than 0."})

    if candidate_set_draft is None:
        issues.append({"severity": "error", "code": "missing_candidate_draft", "message": "Generate candidate architectures in C2 before running optimizer."})
    else:
        if selected_candidates_total <= 0:
            issues.append(
                {
                    "severity": "error",
                    "code": "no_candidates_selected_for_tests",
                    "message": "Select at least one candidate for tests in C2.",
                }
            )
        if compile_gate_status != "ready":
            issues.append(
                {
                    "severity": "error",
                    "code": "compile_gate_not_ready",
                    "message": "Candidate compile gate is not ready. Run `Select for tests` in C2 first.",
                }
            )

    if not isinstance(assigned_dataset_ids, list) or len(assigned_dataset_ids) <= 0:
        issues.append({"severity": "error", "code": "missing_assigned_dataset", "message": "Assign at least one dataset in C4 before optimizer launch."})

    evaluation_profile = _find_target_evaluation_profile(studio_state=evaluation_state, profile_id=None)
    evaluation_report = _build_evaluation_profile_validation_report(profile=evaluation_profile)
    if str(evaluation_report.get("status", "")) == "invalid":
        issues.append({"severity": "error", "code": "evaluation_profile_invalid", "message": "C4 evaluation profile is invalid. Fix C4 issues first."})
    elif str(evaluation_report.get("status", "")) == "warnings":
        issues.append(
            {
                "severity": "warning",
                "code": "evaluation_profile_warnings",
                "message": "C4 evaluation profile has warnings; launch is allowed but quality may be unstable.",
            }
        )

    return issues


def _count_candidates_selected_for_tests(candidate_set_draft: dict[str, Any] | None) -> int:
    """Подсчитывает выбранных кандидатов `selected_for_tests` в candidate set."""

    if not isinstance(candidate_set_draft, dict):
        return 0
    candidates = candidate_set_draft.get("candidates", [])
    if not isinstance(candidates, list):
        return 0
    return len([item for item in candidates if isinstance(item, dict) and bool(item.get("selected_for_tests", False))])


def _extract_candidate_compile_gate_status(candidate_set_draft: dict[str, Any] | None) -> str:
    """Извлекает статус compile gate из candidate set draft."""

    if not isinstance(candidate_set_draft, dict):
        return "missing"
    compile_gate = candidate_set_draft.get("compile_gate", {})
    if not isinstance(compile_gate, dict):
        return "missing"
    return str(compile_gate.get("status", "")).strip() or "missing"
