"""Integration-тесты frontend dev server (static shell + capability API)."""

from __future__ import annotations

import json
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
    """Проверяет, что dev server отдает workbench shell, capability-каталог и реальный C1 endpoint."""

    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [sys.executable, "-m", "optimizer.frontend.dev_server", "--host", "127.0.0.1", "--port", str(port)],
        cwd=_project_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_until_server_ready(base_url)

        with urlopen(f"{base_url}/", timeout=5.0) as response:
            html = response.read().decode("utf-8")
            assert response.status == 200
            assert "C1 Workbench" in html
            assert "id=\"capability-nav\"" in html
            assert "/design_system/colors_and_type.css" in html

        with urlopen(f"{base_url}/api/capabilities", timeout=5.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert payload["version"] == "capability_catalog_v1"
            assert payload["ux_reference"] == "design_system/screenshots/app-v3.png"
            assert len(payload["capabilities"]) == 6
            assert payload["capabilities"][0]["id"] == "c1"
            assert payload["capabilities"][0]["status"] == "enabled"

        status_ok, c1_payload = _json_post(
            f"{base_url}/api/c1/validate-compile",
            {"dsl_file": "examples/dsl/style_direct_llm.yaml"},
        )
        assert status_ok == 200
        assert c1_payload["status"] == "success"
        assert c1_payload["compile_summary"]["status"] == "success"

        status_bad, bad_payload = _json_post(
            f"{base_url}/api/c1/validate-compile",
            {"dsl_file": "examples/dsl/not_exists.yaml"},
        )
        assert status_bad == 400
        assert bad_payload["status"] == "error"

        status_escape, escape_payload = _json_post(
            f"{base_url}/api/c1/validate-compile",
            {"dsl_file": "..\\..\\Windows\\system.ini"},
        )
        assert status_escape == 400
        assert escape_payload["status"] == "error"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
