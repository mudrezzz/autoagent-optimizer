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
    """Проверяет, что dev server отдает shell и вертикальный API-контур C1..C5."""

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
            assert len(payload["capabilities"]) == 9
            assert payload["capabilities"][0]["id"] == "c1"
            assert payload["capabilities"][0]["name"] == "Battle Registry"
            assert payload["capabilities"][0]["status"] == "enabled"
            c2 = next(item for item in payload["capabilities"] if item["id"] == "c2")
            assert c2["status"] == "enabled"
            c3 = next(item for item in payload["capabilities"] if item["id"] == "c3")
            assert c3["status"] == "enabled"
            c4 = next(item for item in payload["capabilities"] if item["id"] == "c4")
            assert c4["status"] == "enabled"
            c5 = next(item for item in payload["capabilities"] if item["id"] == "c5")
            assert c5["status"] == "enabled"
            c5s = next(item for item in payload["capabilities"] if item["id"] == "c5s")
            assert c5s["status"] == "enabled"

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

        status_c4_state_empty, c4_state_empty_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/datasets/state")
        assert status_c4_state_empty == 200
        assert c4_state_empty_payload["status"] == "success"
        assert c4_state_empty_payload["active_dataset"] is None
        assert c4_state_empty_payload["assigned_dataset_ids"] == []
        assert c4_state_empty_payload["datasets"] == []

        status_c4_create, c4_create_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/datasets/create",
            {"name": "stylizer-dataset", "description": "Dataset for C4 smoke"},
        )
        assert status_c4_create == 201
        assert c4_create_payload["status"] == "success"
        dataset_id = str(c4_create_payload["dataset"]["dataset_id"])
        assert c4_create_payload["active_dataset_id"] == dataset_id
        assert c4_create_payload["assigned_dataset_ids"] == []

        status_c4_add_row, c4_add_row_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/datasets/{dataset_id}/rows/add",
            {"row": {"case_id": "case_001", "input": "input text", "expected": "expected text", "notes": "n"}},
        )
        assert status_c4_add_row == 200
        assert c4_add_row_payload["status"] == "success"
        assert c4_add_row_payload["active_dataset"]["rows_total"] == 1
        assert c4_add_row_payload["row"]["target_stage"] == "final"
        assert c4_add_row_payload["row"]["expected_payload"]["answer"] == "expected text"

        status_c4_validate, c4_validate_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/datasets/{dataset_id}/validate",
            {},
        )
        assert status_c4_validate == 200
        assert c4_validate_payload["status"] == "success"
        assert c4_validate_payload["validation_report"]["rows_total"] == 1

        status_c4_save_version, c4_save_version_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/datasets/{dataset_id}/save-version",
            {"label": "v1", "source": "manual"},
        )
        assert status_c4_save_version == 200
        assert c4_save_version_payload["status"] == "success"
        assert c4_save_version_payload["version"]["label"] == "v1"

        status_c4_replace_rows, c4_replace_rows_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/datasets/{dataset_id}/rows/replace",
            {
                "rows": [
                    {
                        "case_id": "case_010",
                        "input": "i1",
                        "target_stage": "retrieval",
                        "expected_payload": {"evidence_ids": ["doc_1", "doc_2"]},
                        "notes": "",
                    },
                    {"case_id": "case_011", "input": "i2", "expected": "e2", "notes": ""},
                ]
            },
        )
        assert status_c4_replace_rows == 200
        assert c4_replace_rows_payload["status"] == "success"
        assert c4_replace_rows_payload["active_dataset"]["rows_total"] == 2
        assert len(c4_replace_rows_payload["datasets"][0]["preview_rows"]) == 2
        assert c4_replace_rows_payload["active_dataset"]["rows"][0]["target_stage"] == "retrieval"
        assert c4_replace_rows_payload["active_dataset"]["rows"][0]["expected_payload"]["evidence_ids"] == ["doc_1", "doc_2"]

        status_c4_assign, c4_assign_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/datasets/assign",
            {
                "dataset_ids": [dataset_id],
            },
        )
        assert status_c4_assign == 200
        assert c4_assign_payload["status"] == "success"
        assert c4_assign_payload["assigned_dataset_ids"] == [dataset_id]

        status_eval_state, eval_state_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/evaluation/state")
        assert status_eval_state == 200
        assert eval_state_payload["status"] == "success"
        assert len(eval_state_payload["comparative_metrics"]) >= 1
        assert len(eval_state_payload["diagnostic_signals"]) >= 1
        assert len(eval_state_payload["evaluators"]) >= 1
        assert isinstance(eval_state_payload["stage_mappings"], list)
        assert isinstance(eval_state_payload["stage_mapping_coverage"], list)
        assert isinstance(eval_state_payload["evaluator_metric_links"], list)
        assert isinstance(eval_state_payload["stage_bindings"], list)
        assert isinstance(eval_state_payload["stage_binding_coverage"], list)
        assert isinstance(eval_state_payload["candidate_features"], dict)
        assert eval_state_payload["candidate_features"]["llm"] is False
        assert eval_state_payload["candidate_features"]["retrieval"] is False

        status_eval_metrics_save, eval_metrics_save_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/metrics/save",
            {
                "comparative_metrics": [
                    {"metric_id": "quality_f1", "title": "Quality F1@K", "description": "quality", "enabled": True, "weight": 0.7},
                    {"metric_id": "cost_per_case", "title": "Cost / case", "description": "cost", "enabled": True, "weight": 0.3},
                ],
                "diagnostic_signals": [
                    {"signal_id": "retrieval_coverage", "title": "Retrieval coverage", "description": "retrieval", "enabled": True},
                ],
            },
        )
        assert status_eval_metrics_save == 200
        assert eval_metrics_save_payload["status"] == "success"
        assert eval_metrics_save_payload["comparative_metrics"][0]["weight"] == 0.7
        assert eval_metrics_save_payload["diagnostic_signals"][0]["availability_status"] == "unavailable"
        assert eval_metrics_save_payload["diagnostic_signals"][0]["enabled"] is False

        status_eval_evaluators_save, eval_evaluators_save_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/evaluators/save",
            {
                "evaluators": [
                    {"evaluator_id": "golden_oracle", "title": "Golden dataset oracle", "description": "deterministic", "enabled": True},
                    {"evaluator_id": "llm_judge", "title": "LLM as a judge", "description": "semantic", "enabled": True},
                ]
            },
        )
        assert status_eval_evaluators_save == 200
        assert eval_evaluators_save_payload["status"] == "success"
        assert len(eval_evaluators_save_payload["evaluators"]) == 2

        status_eval_matrix_save, eval_matrix_save_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/matrix/save",
            {
                "evaluator_metric_links": [
                    {"evaluator_id": "golden_oracle", "metric_kind": "comparative", "metric_id": "quality_f1", "enabled": True},
                    {"evaluator_id": "golden_oracle", "metric_kind": "diagnostic", "metric_id": "synthesis_drift", "enabled": True},
                    {"evaluator_id": "llm_judge", "metric_kind": "comparative", "metric_id": "quality_f1", "enabled": False},
                ]
            },
        )
        assert status_eval_matrix_save == 200
        assert eval_matrix_save_payload["status"] == "success"
        assert isinstance(eval_matrix_save_payload["evaluator_metric_links"], list)

        status_eval_budget_save, eval_budget_save_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/budget/save",
            {
                "budget": {"max_cases": 12, "max_llm_calls": 40, "max_cost_usd": 1.5},
            },
        )
        assert status_eval_budget_save == 200
        assert eval_budget_save_payload["status"] == "success"
        assert eval_budget_save_payload["budget"]["max_cases"] == 12

        status_eval_validate, eval_validate_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/validate",
            {},
        )
        assert status_eval_validate == 200
        assert eval_validate_payload["status"] == "success"
        assert eval_validate_payload["validation_report"]["status"] in {"ready", "warnings", "invalid"}

        status_eval_save_version, eval_save_version_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/save-version",
            {"label": "eval-v1", "source": "manual"},
        )
        assert status_eval_save_version == 200
        assert eval_save_version_payload["status"] == "success"
        assert eval_save_version_payload["version"]["label"] == "eval-v1"

        status_optimizer_state, optimizer_state_payload = _json_get(f"{base_url}/api/arenas/{arena_id}/optimizer/state")
        assert status_optimizer_state == 200
        assert optimizer_state_payload["status"] == "success"
        assert len(optimizer_state_payload["methods"]) >= 1
        assert len(optimizer_state_payload["controls"]) >= 1

        status_optimizer_save, optimizer_save_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/optimizer/save",
            {
                "methods": [
                    {"method_id": "random_search", "title": "Random search", "description": "baseline", "enabled": True},
                    {"method_id": "grid_search", "title": "Grid search", "description": "deterministic", "enabled": True},
                ],
                "controls": [
                    {"control_id": "tune_prompts", "title": "Tune prompts", "description": "scope", "enabled": True},
                    {"control_id": "tune_pattern_mix", "title": "Tune pattern mix", "description": "scope", "enabled": True},
                ],
                "run_plan": {"epochs_total": 3, "candidates_per_epoch": 4, "max_parallel_trials": 2, "early_stop_patience": 1},
                "budget": {"max_cases": 24, "max_llm_calls": 200, "max_cost_usd": 8.0, "max_runtime_minutes": 30},
            },
        )
        assert status_optimizer_save == 200
        assert optimizer_save_payload["status"] == "success"
        assert optimizer_save_payload["run_plan"]["epochs_total"] == 3

        status_optimizer_validate, optimizer_validate_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/optimizer/validate",
            {},
        )
        assert status_optimizer_validate == 200
        assert optimizer_validate_payload["status"] == "success"
        assert optimizer_validate_payload["validation_report"]["status"] in {"ready", "warnings", "invalid"}

        status_optimizer_version, optimizer_version_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/optimizer/save-version",
            {"label": "opt-v1", "source": "manual"},
        )
        assert status_optimizer_version == 200
        assert optimizer_version_payload["status"] == "success"
        assert optimizer_version_payload["version"]["label"] == "opt-v1"

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
            f"{base_url}/api/arenas/{arena_id}/candidates/select-for-tests",
            {
                "candidate_ids": [
                    "cand_pattern_cleaner_v0",
                ],
                "max_compile_attempts": 3,
            },
        )
        assert status_compile_gate == 200
        assert compile_gate_payload["status"] == "success"
        assert compile_gate_payload["action"] == "select_candidates_for_tests"
        assert compile_gate_payload["compile_gate"]["status"] in {"ready", "failed"}
        assert compile_gate_payload["compile_gate"]["compiled_candidates"] == 1
        assert compile_gate_payload["compile_gate"]["selected_candidates"] == 1
        assert compile_gate_payload["candidate_set_draft"]["compile_gate"]["status"] == compile_gate_payload["compile_gate"]["status"]
        assert compile_gate_payload["messages_total"] >= 3

        status_eval_stage_auto, eval_stage_auto_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/stage-mapping/auto-map",
            {},
        )
        assert status_eval_stage_auto == 200
        assert eval_stage_auto_payload["status"] == "success"
        assert eval_stage_auto_payload["action"] == "auto_map_stage_mappings"
        assert isinstance(eval_stage_auto_payload["suggested_stage_mappings"], list)
        assert isinstance(eval_stage_auto_payload["suggested_stage_mapping_coverage"], list)

        status_eval_stage_save, eval_stage_save_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/evaluation/stage-mapping/save",
            {
                "stage_mappings": eval_stage_auto_payload["suggested_stage_mappings"],
            },
        )
        assert status_eval_stage_save == 200
        assert eval_stage_save_payload["status"] == "success"
        assert eval_stage_save_payload["action"] == "save_stage_mappings"
        assert isinstance(eval_stage_save_payload["stage_mappings"], list)
        assert isinstance(eval_stage_save_payload["stage_mapping_coverage"], list)

        status_optimizer_validate_after_compile, optimizer_validate_after_compile_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/optimizer/validate",
            {},
        )
        assert status_optimizer_validate_after_compile == 200
        assert optimizer_validate_after_compile_payload["status"] == "success"
        assert optimizer_validate_after_compile_payload["validation_report"]["status"] in {"ready", "warnings"}

        status_optimizer_launch, optimizer_launch_payload = _json_post(
            f"{base_url}/api/arenas/{arena_id}/optimizer/launch",
            {"triggered_by": "integration_test"},
        )
        assert status_optimizer_launch == 202
        assert optimizer_launch_payload["status"] == "success"
        assert optimizer_launch_payload["run"]["status"] == "queued"
        assert optimizer_launch_payload["run"]["triggered_by"] == "integration_test"

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
