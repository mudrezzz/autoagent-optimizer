"""Файловое хранилище workspace/project для C1 vertical slice."""

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
    """Потокобезопасный JSON-store workspace/project сущностей."""

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
                records.append(
                    WorkspaceRecord(
                        workspace_id=str(item["workspace_id"]),
                        name=str(item["name"]),
                        description=str(item.get("description", "")),
                        created_at=str(item["created_at"]),
                        tenant_id=str(item.get("tenant_id", "")),
                        owner_user_id=str(item.get("owner_user_id", "")),
                    )
                )
            return records

    def create_workspace(self, *, tenant_id: str, owner_user_id: str, name: str, description: str) -> WorkspaceRecord:
        """Создает новый workspace и сохраняет его в JSON-store."""

        normalized_name = name.strip()
        normalized_description = description.strip()
        if not normalized_name:
            raise ValueError("Workspace name must be a non-empty string.")

        with self._lock:
            data = self._read_store()
            workspaces = data.get("workspaces", [])
            for item in workspaces:
                if (
                    str(item.get("tenant_id", "")) == tenant_id
                    and str(item.get("owner_user_id", "")) == owner_user_id
                    and str(item.get("name", "")).strip().lower() == normalized_name.lower()
                ):
                    raise ValueError("Workspace with the same name already exists.")

            now = _utc_now_iso()
            workspace = {
                "workspace_id": f"ws_{uuid4().hex[:10]}",
                "name": normalized_name,
                "description": normalized_description,
                "created_at": now,
                "tenant_id": tenant_id,
                "owner_user_id": owner_user_id,
                "projects": [],
            }
            workspaces.append(workspace)
            data["workspaces"] = workspaces
            self._write_store(data)
            return WorkspaceRecord(
                workspace_id=str(workspace["workspace_id"]),
                name=str(workspace["name"]),
                description=str(workspace["description"]),
                created_at=str(workspace["created_at"]),
                tenant_id=str(workspace["tenant_id"]),
                owner_user_id=str(workspace["owner_user_id"]),
            )

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
                ProjectRecord(
                    project_id=str(item["project_id"]),
                    workspace_id=str(item["workspace_id"]),
                    name=str(item["name"]),
                    description=str(item.get("description", "")),
                    status=str(item.get("status", "draft")),
                    created_at=str(item["created_at"]),
                    updated_at=str(item["updated_at"]),
                    tenant_id=str(item.get("tenant_id", "")),
                    owner_user_id=str(item.get("owner_user_id", "")),
                )
                for item in projects
                if str(item.get("tenant_id", "")) == tenant_id and str(item.get("owner_user_id", "")) == owner_user_id
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
                if str(item.get("name", "")).strip().lower() == normalized_name.lower():
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
            }
            projects.append(project)
            workspace["projects"] = projects
            self._write_store(data)
            return ProjectRecord(
                project_id=str(project["project_id"]),
                workspace_id=str(project["workspace_id"]),
                name=str(project["name"]),
                description=str(project["description"]),
                status=str(project["status"]),
                created_at=str(project["created_at"]),
                updated_at=str(project["updated_at"]),
                tenant_id=str(project["tenant_id"]),
                owner_user_id=str(project["owner_user_id"]),
            )

    def get_project(self, *, tenant_id: str, owner_user_id: str, project_id: str) -> ProjectRecord:
        """Возвращает tenant/user-scoped project по идентификатору."""

        with self._lock:
            data = self._read_store()
            for workspace in data.get("workspaces", []):
                for item in workspace.get("projects", []):
                    if (
                        str(item.get("project_id")) == project_id
                        and str(item.get("tenant_id", "")) == tenant_id
                        and str(item.get("owner_user_id", "")) == owner_user_id
                    ):
                        return ProjectRecord(
                            project_id=str(item["project_id"]),
                            workspace_id=str(item["workspace_id"]),
                            name=str(item["name"]),
                            description=str(item.get("description", "")),
                            status=str(item.get("status", "draft")),
                            created_at=str(item["created_at"]),
                            updated_at=str(item["updated_at"]),
                            tenant_id=str(item.get("tenant_id", "")),
                            owner_user_id=str(item.get("owner_user_id", "")),
                        )
        raise KeyError(f"Project not found: {project_id}")

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


def _utc_now_iso() -> str:
    """Возвращает UTC timestamp в ISO-формате для audit-полей сущностей."""

    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
