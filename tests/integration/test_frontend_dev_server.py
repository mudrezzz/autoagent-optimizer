"""Integration-тесты frontend dev server (static shell + capability API)."""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь к корню проекта."""

    return Path(__file__).resolve().parents[2]


def _find_free_port() -> int:
    """Выделяет свободный TCP-порт для запуска тестового HTTP-сервера."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_until_server_ready(base_url: str, *, timeout_sec: float = 15.0) -> None:
    """Ждет успешного ответа `/api/health`, чтобы избежать race-condition после старта сервера."""

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urlopen(f"{base_url}/api/health", timeout=1.5) as response:
                if response.status == 200:
                    return
        except URLError:
            time.sleep(0.25)
    raise AssertionError("Frontend dev server did not become ready in time.")


def _json_post(
    url: str,
    payload: dict[str, object],
    *,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, object]]:
    """Выполняет JSON POST и возвращает `(status_code, payload)` даже при HTTP 4xx/5xx."""

    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url=url, data=raw, method="POST")
    request.add_header("Content-Type", "application/json; charset=utf-8")
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urlopen(request, timeout=5.0) as response:
            body = json.loads(response.read().decode("utf-8"))
            return int(response.status), body
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        return int(exc.code), body


def _json_get(url: str, *, headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
    """Выполняет JSON GET и возвращает `(status_code, payload)` даже при HTTP 4xx/5xx."""

    request = Request(url=url, method="GET")
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urlopen(request, timeout=5.0) as response:
            body = json.loads(response.read().decode("utf-8"))
            return int(response.status), body
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        return int(exc.code), body


@pytest.mark.integration
def test_frontend_dev_server_serves_shell_and_capability_api() -> None:
    """Проверяет, что dev server отдает workbench shell, capability-каталог и C1 workspace/project API."""

    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    store_file = _project_root() / "tmp" / "tests" / "frontend_dev_server_registry.json"
    store_file.parent.mkdir(parents=True, exist_ok=True)
    if store_file.exists():
        store_file.unlink()

    env = os.environ.copy()
    env["AUTOAGENT_WORKSPACE_STORE_FILE"] = str(store_file)

    proc = subprocess.Popen(
        [sys.executable, "-m", "optimizer.frontend.dev_server", "--host", "127.0.0.1", "--port", str(port)],
        cwd=_project_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        _wait_until_server_ready(base_url)

        with urlopen(f"{base_url}/", timeout=5.0) as response:
            html = response.read().decode("utf-8")
            assert response.status == 200
            assert "Workspace Registry" in html
            assert "id=\"root\"" in html
            assert "/design_system/colors_and_type.css" in html
            match = re.search(r'"/assets/[^"]+\.js"', html)
            assert match is not None
            asset_path = match.group(0).strip("\"")

        with urlopen(f"{base_url}{asset_path}", timeout=5.0) as response:
            assert response.status == 200

        with urlopen(f"{base_url}/api/capabilities", timeout=5.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert payload["version"] == "capability_catalog_v1"
            assert payload["ux_reference"] == "design_system/screenshots/app-v3.png"
            assert len(payload["capabilities"]) == 6
            assert payload["capabilities"][0]["id"] == "c1"
            assert payload["capabilities"][0]["name"] == "Workspace & Projects"
            assert payload["capabilities"][0]["status"] == "enabled"

        status_workspaces, workspaces_payload = _json_get(f"{base_url}/api/workspaces")
        assert status_workspaces == 200
        assert workspaces_payload["status"] == "success"
        assert workspaces_payload["total"] == 0
        assert workspaces_payload["tenant_id"] == "tenant_demo_1"
        assert workspaces_payload["owner_user_id"] == "user_demo_1"

        status_create_workspace, workspace_payload = _json_post(
            f"{base_url}/api/workspaces",
            {"name": "support-qa", "description": "Support experiments"},
        )
        assert status_create_workspace == 201
        assert workspace_payload["status"] == "success"
        workspace_id = str(workspace_payload["workspace"]["workspace_id"])
        assert workspace_payload["workspace"]["tenant_id"] == "tenant_demo_1"
        assert workspace_payload["workspace"]["owner_user_id"] == "user_demo_1"

        status_create_project, project_payload = _json_post(
            f"{base_url}/api/workspaces/{workspace_id}/projects",
            {"name": "support-qa.v1", "description": "Project v1"},
        )
        assert status_create_project == 201
        assert project_payload["status"] == "success"
        project_id = str(project_payload["project"]["project_id"])
        assert project_payload["project"]["tenant_id"] == "tenant_demo_1"
        assert project_payload["project"]["owner_user_id"] == "user_demo_1"

        status_projects, projects_list_payload = _json_get(f"{base_url}/api/workspaces/{workspace_id}/projects")
        assert status_projects == 200
        assert projects_list_payload["status"] == "success"
        assert projects_list_payload["total"] == 1
        assert projects_list_payload["tenant_id"] == "tenant_demo_1"
        assert projects_list_payload["owner_user_id"] == "user_demo_1"

        status_project, project_get_payload = _json_get(f"{base_url}/api/projects/{project_id}")
        assert status_project == 200
        assert project_get_payload["status"] == "success"
        assert project_get_payload["project"]["project_id"] == project_id

        status_rename_workspace, renamed_payload = _json_post(
            f"{base_url}/api/workspaces/{workspace_id}/rename",
            {"name": "support-qa-renamed"},
        )
        assert status_rename_workspace == 200
        assert renamed_payload["workspace"]["name"] == "support-qa-renamed"

        status_duplicate_workspace, duplicate_workspace_payload = _json_post(
            f"{base_url}/api/workspaces/{workspace_id}/duplicate",
            {},
        )
        assert status_duplicate_workspace == 201
        assert duplicate_workspace_payload["status"] == "success"
        duplicated_workspace_id = str(duplicate_workspace_payload["workspace"]["workspace_id"])
        assert duplicated_workspace_id != workspace_id

        status_delete_workspace, delete_payload = _json_post(
            f"{base_url}/api/workspaces/{workspace_id}/delete",
            {},
        )
        assert status_delete_workspace == 200
        assert delete_payload["workspace_id"] == workspace_id

        status_projects_deleted, deleted_projects_payload = _json_get(
            f"{base_url}/api/workspaces/{workspace_id}/projects",
        )
        assert status_projects_deleted == 404
        assert deleted_projects_payload["status"] == "error"

        status_projects_duplicated, duplicated_projects_payload = _json_get(
            f"{base_url}/api/workspaces/{duplicated_workspace_id}/projects",
        )
        assert status_projects_duplicated == 200
        assert duplicated_projects_payload["total"] == 0

        status_duplicate_workspace, duplicate_workspace_payload = _json_post(
            f"{base_url}/api/workspaces",
            {"name": "support-qa", "description": "duplicate"},
        )
        assert status_duplicate_workspace == 201
        assert duplicate_workspace_payload["status"] == "success"

        status_missing_workspace, missing_workspace_payload = _json_post(
            f"{base_url}/api/workspaces/ws_missing/projects",
            {"name": "support-qa.v2", "description": ""},
        )
        assert status_missing_workspace == 404
        assert missing_workspace_payload["status"] == "error"

        # Русский комментарий: второй tenant не видит данные первого tenant и может создать одноименный workspace.
        second_actor_headers = {
            "X-Demo-Tenant-Id": "tenant_demo_2",
            "X-Demo-User-Id": "user_demo_2",
        }
        status_workspaces_second, second_workspaces_payload = _json_get(
            f"{base_url}/api/workspaces",
            headers=second_actor_headers,
        )
        assert status_workspaces_second == 200
        assert second_workspaces_payload["total"] == 0

        status_create_workspace_second, workspace_payload_second = _json_post(
            f"{base_url}/api/workspaces",
            {"name": "support-qa", "description": "Second tenant scope"},
            headers=second_actor_headers,
        )
        assert status_create_workspace_second == 201
        workspace_id_second = str(workspace_payload_second["workspace"]["workspace_id"])

        status_forbidden_cross_tenant, cross_tenant_project_payload = _json_post(
            f"{base_url}/api/workspaces/{workspace_id}/projects",
            {"name": "support-qa.v2", "description": "wrong scope"},
            headers=second_actor_headers,
        )
        assert status_forbidden_cross_tenant == 404
        assert cross_tenant_project_payload["status"] == "error"

        status_projects_second, projects_second_payload = _json_get(
            f"{base_url}/api/workspaces/{workspace_id_second}/projects",
            headers=second_actor_headers,
        )
        assert status_projects_second == 200
        assert projects_second_payload["total"] == 0

        # Русский комментарий: legacy C1 endpoint остается доступным как debug-route.
        status_legacy, legacy_payload = _json_post(
            f"{base_url}/api/c1/validate-compile",
            {"dsl_file": "examples/dsl/style_direct_llm.yaml"},
        )
        assert status_legacy == 200
        assert legacy_payload["status"] == "success"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        if store_file.exists():
            store_file.unlink()
