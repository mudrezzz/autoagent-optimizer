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


def _json_post(url: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    """Выполняет JSON POST и возвращает `(status_code, payload)` даже при HTTP 4xx/5xx."""

    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url=url, data=raw, method="POST")
    request.add_header("Content-Type", "application/json; charset=utf-8")
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

        with urlopen(f"{base_url}/api/workspaces", timeout=5.0) as response:
            workspaces_payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert workspaces_payload["status"] == "success"
            assert workspaces_payload["total"] == 0

        status_create_workspace, workspace_payload = _json_post(
            f"{base_url}/api/workspaces",
            {"name": "support-qa", "description": "Support experiments"},
        )
        assert status_create_workspace == 201
        assert workspace_payload["status"] == "success"
        workspace_id = str(workspace_payload["workspace"]["workspace_id"])

        status_create_project, project_payload = _json_post(
            f"{base_url}/api/workspaces/{workspace_id}/projects",
            {"name": "support-qa.v1", "description": "Project v1"},
        )
        assert status_create_project == 201
        assert project_payload["status"] == "success"
        project_id = str(project_payload["project"]["project_id"])

        with urlopen(f"{base_url}/api/workspaces/{workspace_id}/projects", timeout=5.0) as response:
            projects_list_payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert projects_list_payload["status"] == "success"
            assert projects_list_payload["total"] == 1

        with urlopen(f"{base_url}/api/projects/{project_id}", timeout=5.0) as response:
            project_get_payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert project_get_payload["status"] == "success"
            assert project_get_payload["project"]["project_id"] == project_id

        status_duplicate_workspace, duplicate_workspace_payload = _json_post(
            f"{base_url}/api/workspaces",
            {"name": "support-qa", "description": "duplicate"},
        )
        assert status_duplicate_workspace == 409
        assert duplicate_workspace_payload["status"] == "error"

        status_missing_workspace, missing_workspace_payload = _json_post(
            f"{base_url}/api/workspaces/ws_missing/projects",
            {"name": "support-qa.v2", "description": ""},
        )
        assert status_missing_workspace == 404
        assert missing_workspace_payload["status"] == "error"

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
