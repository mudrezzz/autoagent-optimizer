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
