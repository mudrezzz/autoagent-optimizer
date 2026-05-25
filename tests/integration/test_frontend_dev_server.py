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


def _json_post(url: str, payload: dict[str, object], *, headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
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
    """Проверяет, что dev server отдает shell, capability-каталог и C1+C2 arena API-контур."""

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
            assert "Battles Hub" in html
            assert "id=\"root\"" in html
            assert "/design_system/colors_and_type.css" in html
            match = re.search(r'"/assets/[^"]+\.js"', html)
            assert match is not None
            asset_path = match.group(0).strip('"')

        with urlopen(f"{base_url}{asset_path}", timeout=5.0) as response:
            assert response.status == 200

        with urlopen(f"{base_url}/api/capabilities", timeout=5.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert payload["version"] == "capability_catalog_v1"
            assert payload["ux_reference"] == "design_system/screenshots/app-v3.png"
            assert len(payload["capabilities"]) == 6
            assert payload["capabilities"][0]["id"] == "c1"
            assert payload["capabilities"][0]["name"] == "Battle Registry"
            assert payload["capabilities"][0]["status"] == "enabled"
            c2 = next(item for item in payload["capabilities"] if item["id"] == "c2")
            assert c2["status"] == "enabled"
            c3 = next(item for item in payload["capabilities"] if item["id"] == "c3")
            assert c3["status"] == "enabled"

        status_arenas, arenas_payload = _json_get(f"{base_url}/api/arenas")
        assert status_arenas == 200
        assert arenas_payload["status"] == "success"
        assert arenas_payload["total"] == 0
        assert arenas_payload["tenant_id"] == "tenant_demo_1"
        assert arenas_payload["owner_user_id"] == "user_demo_1"

        status_create_arena, arena_payload = _json_post(
            f"{base_url}/api/arenas",
            {"name": "support-qa", "description": "Support experiments"},
        )
        assert status_create_arena == 201
        assert arena_payload["status"] == "success"
        arena_id = str(arena_payload["arena"]["workspace_id"])
        assert arena_payload["arena"]["tenant_id"] == "tenant_demo_1"
        assert arena_payload["arena"]["owner_user_id"] == "user_demo_1"

        status_get_arena, get_arena_payload = _json_get(f"{base_url}/api/arenas/{arena_id}")
        assert status_get_arena == 200
        assert get_arena_payload["status"] == "success"
        assert get_arena_payload["arena"]["workspace_id"] == arena_id

        status_chat_state_empty, chat_state_empty_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/chat/state")
        assert status_chat_state_empty == 200
        assert chat_state_empty_payload["status"] == "success"
        assert chat_state_empty_payload["messages_total"] == 0
        assert chat_state_empty_payload["candidate_set_draft"] is None

        status_c3_selection, c3_selection_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/patterns/selection")
        assert status_c3_selection == 200
        assert c3_selection_payload["status"] == "success"
        assert c3_selection_payload["selection"]["include_pattern_ids"] == []
        assert c3_selection_payload["selection"]["exclude_pattern_ids"] == []

        status_c3_search, c3_search_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/patterns/search?q=rewrite&limit=5")
        assert status_c3_search == 200
        assert c3_search_payload["status"] == "success"
        assert c3_search_payload["returned"] >= 1

        status_c3_update, c3_update_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/patterns/selection",
            {
                "include_pattern_ids": ["style.pattern_cleaner"],
                "exclude_pattern_ids": ["style.hitl_reviewer"],
            },
        )
        assert status_c3_update == 200
        assert c3_update_payload["selection"]["include_pattern_ids"] == ["style.pattern_cleaner"]
        assert c3_update_payload["selection"]["exclude_pattern_ids"] == ["style.hitl_reviewer"]

        status_chat_message, chat_message_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/chat/messages",
            {
                "message": "Нужен агент для стилизации постов в живой тон.",
                "generate_candidates": True,
                "max_candidates": 3,
            },
        )
        assert status_chat_message == 201
        assert chat_message_payload["status"] == "success"
        assert chat_message_payload["messages_total"] >= 2
        assert chat_message_payload["candidate_set_draft"] is not None
        assert chat_message_payload["candidate_set_draft"]["total"] == 1
        assert chat_message_payload["candidate_set_draft"]["source_patterns"] == ["style.pattern_cleaner"]

        status_chat_state, chat_state_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/chat/state")
        assert status_chat_state == 200
        assert chat_state_payload["messages_total"] >= 2
        assert chat_state_payload["candidate_set_draft"]["arena_id"] == arena_id
        assert chat_state_payload["candidate_set_draft"]["compile_gate"]["status"] == "draft"

        status_compile_gate, compile_gate_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/candidates/assemble-compile",
            {},
        )
        assert status_compile_gate == 200
        assert compile_gate_payload["status"] == "success"
        assert compile_gate_payload["action"] == "assemble_compile_candidates"
        assert compile_gate_payload["compile_gate"]["status"] in {"ready", "failed"}
        assert compile_gate_payload["compile_gate"]["compiled_candidates"] == compile_gate_payload["compile_gate"]["total_candidates"]
        assert compile_gate_payload["candidate_set_draft"]["compile_gate"]["status"] == compile_gate_payload["compile_gate"]["status"]
        assert compile_gate_payload["messages_total"] >= 3

        status_rename_arena, renamed_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/rename",
            {"name": "support-qa-renamed"},
        )
        assert status_rename_arena == 200
        assert renamed_payload["arena"]["name"] == "support-qa-renamed"

        status_duplicate_arena, duplicate_arena_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/duplicate",
            {},
        )
        assert status_duplicate_arena == 201
        duplicated_arena_id = str(duplicate_arena_payload["arena"]["workspace_id"])
        assert duplicated_arena_id != arena_id

        status_delete_arena, delete_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/delete",
            {},
        )
        assert status_delete_arena == 200
        assert delete_payload["arena_id"] == arena_id

        status_missing_arena, missing_arena_payload = _json_get(f"{base_url}/api/arenas/{arena_id}")
        assert status_missing_arena == 404
        assert missing_arena_payload["status"] == "error"

        # Русский комментарий: второй tenant не видит данные первого tenant и может создать одноименную арену.
        second_actor_headers = {
            "X-Demo-Tenant-Id": "tenant_demo_2",
            "X-Demo-User-Id": "user_demo_2",
        }
        status_arenas_second, second_arenas_payload = _json_get(f"{base_url}/api/arenas", headers=second_actor_headers)
        assert status_arenas_second == 200
        assert second_arenas_payload["total"] == 0

        status_create_arena_second, arena_payload_second = _json_post(
            f"{base_url}/api/arenas",
            {"name": "support-qa", "description": "Second tenant scope"},
            headers=second_actor_headers,
        )
        assert status_create_arena_second == 201
        arena_id_second = str(arena_payload_second["arena"]["workspace_id"])

        status_cross_tenant_get, cross_tenant_payload = _json_get(
            f"{base_url}/api/arenas/{duplicated_arena_id}",
            headers=second_actor_headers,
        )
        assert status_cross_tenant_get == 404
        assert cross_tenant_payload["status"] == "error"

        status_get_second, get_second_payload = _json_get(
            f"{base_url}/api/arenas/{arena_id_second}",
            headers=second_actor_headers,
        )
        assert status_get_second == 200
        assert get_second_payload["arena"]["workspace_id"] == arena_id_second

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
