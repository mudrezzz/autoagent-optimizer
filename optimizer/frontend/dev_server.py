"""Dev server frontend shell: статический UI + минимальный API для capability-проверок."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from optimizer.c2 import build_candidate_draft_from_brief, select_candidates_for_tests_and_prepare
from optimizer.c3 import search_pattern_library
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.io import DslLoadError, DslValidationError, load_dsl_spec
from optimizer.frontend.contracts import build_capability_catalog_payload, build_stub_capability_payload
from optimizer.workspace import WorkspaceRegistryStore


class FrontendDevServerCli:
    """CLI-компонент запуска frontend shell dev server."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Создает CLI-парсер для dev server."""

        parser = argparse.ArgumentParser(description="AutoAgent Optimizer frontend shell dev server")
        parser.add_argument("--host", default="127.0.0.1", help="Хост bind для HTTP-сервера.")
        parser.add_argument("--port", type=int, default=4173, help="Порт bind для HTTP-сервера.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Запускает HTTP-сервер и возвращает код завершения процесса."""

        parser = FrontendDevServerCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        store_file = _resolve_workspace_store_file(project_root=project_root)
        registry_store = WorkspaceRegistryStore(store_file=store_file)
        handler_class = _build_handler(project_root=project_root, registry_store=registry_store)
        server = ThreadingHTTPServer((args.host, args.port), handler_class)

        print(f"[FRONTEND] dev server started at http://{args.host}:{args.port}", flush=True)
        print(f"[FRONTEND] registry store: {store_file}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0


def _resolve_workspace_store_file(*, project_root: Path) -> Path:
    """Определяет путь к JSON-store arena/workspace с override через env."""

    raw = os.environ.get("AUTOAGENT_WORKSPACE_STORE_FILE", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (project_root / "tmp" / "workspace_registry.json").resolve()


def _resolve_default_actor() -> tuple[str, str]:
    """Возвращает default tenant/user для dev-режима без полноценной auth."""

    tenant_id = os.environ.get("AUTOAGENT_DEMO_TENANT_ID", "tenant_demo_1").strip() or "tenant_demo_1"
    user_id = os.environ.get("AUTOAGENT_DEMO_USER_ID", "user_demo_1").strip() or "user_demo_1"
    return tenant_id, user_id


def _build_c4_dataset_state_payload(*, arena_id: str, studio_state: dict[str, Any]) -> dict[str, Any]:
    """Формирует публичный API-payload состояния C4 Dataset Studio."""

    datasets = studio_state.get("datasets", [])
    active_dataset_id = str(studio_state.get("active_dataset_id", "")).strip()
    assigned_dataset_ids = studio_state.get("assigned_dataset_ids", [])
    active_dataset = next((item for item in datasets if str(item.get("dataset_id", "")) == active_dataset_id), None)
    return {
        "status": "success",
        "capability_id": "c4",
        "arena_id": arena_id,
        "active_dataset_id": active_dataset_id,
        "assigned_dataset_ids": [str(item) for item in assigned_dataset_ids if isinstance(item, str)],
        "datasets": [_build_c4_dataset_summary(item) for item in datasets if isinstance(item, dict)],
        "active_dataset": _build_c4_dataset_detail(active_dataset) if isinstance(active_dataset, dict) else None,
    }


def _build_c4_dataset_summary(dataset: dict[str, Any]) -> dict[str, Any]:
    """Собирает summary DTO dataset без полного rows_snapshot."""

    versions = dataset.get("versions", [])
    latest_version = versions[-1] if isinstance(versions, list) and versions else None
    rows = dataset.get("rows", [])
    preview_rows = rows[:5] if isinstance(rows, list) else []
    return {
        "dataset_id": str(dataset.get("dataset_id", "")),
        "name": str(dataset.get("name", "")),
        "description": str(dataset.get("description", "")),
        "rows_total": len(rows) if isinstance(rows, list) else 0,
        "versions_total": len(versions) if isinstance(versions, list) else 0,
        "updated_at": str(dataset.get("updated_at", "")),
        "last_version_id": str(latest_version.get("version_id", "")) if isinstance(latest_version, dict) else "",
        "preview_rows": [dict(item) for item in preview_rows if isinstance(item, dict)],
    }


def _build_c4_dataset_detail(dataset: dict[str, Any] | None) -> dict[str, Any] | None:
    """Собирает detail DTO dataset для активной карточки C4 Studio."""

    if not isinstance(dataset, dict):
        return None
    rows = dataset.get("rows", [])
    versions = dataset.get("versions", [])
    return {
        **_build_c4_dataset_summary(dataset),
        "created_at": str(dataset.get("created_at", "")),
        "rows": [dict(item) for item in rows if isinstance(item, dict)] if isinstance(rows, list) else [],
        "versions": [_build_c4_dataset_version(item) for item in versions if isinstance(item, dict)] if isinstance(versions, list) else [],
    }


def _build_c4_dataset_version(version: dict[str, Any]) -> dict[str, Any]:
    """Собирает публичный version DTO без тяжелого rows_snapshot."""

    return {
        "version_id": str(version.get("version_id", "")),
        "label": str(version.get("label", "")),
        "created_at": str(version.get("created_at", "")),
        "rows_total": int(version.get("rows_total", 0) or 0),
        "source": str(version.get("source", "")),
    }


def _build_c4_evaluation_state_payload(*, arena_id: str, studio_state: dict[str, Any]) -> dict[str, Any]:
    """Формирует публичный API-payload состояния C4 Metrics & Evaluators Studio."""

    versions = studio_state.get("versions", [])
    return {
        "status": "success",
        "capability_id": "c4",
        "arena_id": arena_id,
        "comparative_metrics": [dict(item) for item in studio_state.get("comparative_metrics", []) if isinstance(item, dict)],
        "diagnostic_signals": [dict(item) for item in studio_state.get("diagnostic_signals", []) if isinstance(item, dict)],
        "evaluators": [dict(item) for item in studio_state.get("evaluators", []) if isinstance(item, dict)],
        "stage_mappings": [dict(item) for item in studio_state.get("stage_mappings", []) if isinstance(item, dict)],
        "stage_mapping_coverage": [dict(item) for item in studio_state.get("stage_mapping_coverage", []) if isinstance(item, dict)],
        "stage_bindings": [dict(item) for item in studio_state.get("stage_bindings", []) if isinstance(item, dict)],
        "stage_binding_coverage": [dict(item) for item in studio_state.get("stage_binding_coverage", []) if isinstance(item, dict)],
        "evaluator_metric_links": [dict(item) for item in studio_state.get("evaluator_metric_links", []) if isinstance(item, dict)],
        "candidate_features": dict(studio_state.get("candidate_features", {})),
        "budget": dict(studio_state.get("budget", {})),
        "versions": [_build_c4_evaluation_version(item) for item in versions if isinstance(item, dict)],
        "updated_at": str(studio_state.get("updated_at", "")),
    }


def _build_c4_evaluation_version(version: dict[str, Any]) -> dict[str, Any]:
    """Собирает публичный version DTO для evaluation profile без тяжелых деталей."""

    comparative_metrics = version.get("comparative_metrics", [])
    diagnostic_signals = version.get("diagnostic_signals", [])
    evaluators = version.get("evaluators", [])
    stage_bindings = version.get("stage_bindings", [])
    stage_mappings = version.get("stage_mappings", [])
    return {
        "version_id": str(version.get("version_id", "")),
        "label": str(version.get("label", "")),
        "created_at": str(version.get("created_at", "")),
        "source": str(version.get("source", "")),
        "enabled_comparative_total": len([item for item in comparative_metrics if isinstance(item, dict) and bool(item.get("enabled", False))]),
        "enabled_diagnostic_total": len([item for item in diagnostic_signals if isinstance(item, dict) and bool(item.get("enabled", False))]),
        "enabled_evaluators_total": len([item for item in evaluators if isinstance(item, dict) and bool(item.get("enabled", False))]),
        "enabled_stage_bindings_total": len([item for item in stage_bindings if isinstance(item, dict) and bool(item.get("enabled", True))]),
        "enabled_stage_mappings_total": len([item for item in stage_mappings if isinstance(item, dict) and bool(item.get("enabled", True))]),
    }


def _build_c5_optimizer_state_payload(*, arena_id: str, studio_state: dict[str, Any]) -> dict[str, Any]:
    """Формирует публичный API-payload состояния C5 Optimizer Setup Studio."""

    versions = studio_state.get("versions", [])
    launch_history = studio_state.get("launch_history", [])
    return {
        "status": "success",
        "capability_id": "c5",
        "arena_id": arena_id,
        "methods": [dict(item) for item in studio_state.get("methods", []) if isinstance(item, dict)],
        "controls": [dict(item) for item in studio_state.get("controls", []) if isinstance(item, dict)],
        "run_plan": dict(studio_state.get("run_plan", {})),
        "budget": dict(studio_state.get("budget", {})),
        "versions": [_build_c5_optimizer_version(item) for item in versions if isinstance(item, dict)],
        "launch_history": [_build_c5_launch_entry(item) for item in launch_history if isinstance(item, dict)],
        "updated_at": str(studio_state.get("updated_at", "")),
    }


def _build_c5_optimizer_version(version: dict[str, Any]) -> dict[str, Any]:
    """Собирает публичный version DTO для optimizer setup без тяжелых деталей."""

    methods = version.get("methods", [])
    controls = version.get("controls", [])
    run_plan = version.get("run_plan", {})
    return {
        "version_id": str(version.get("version_id", "")),
        "label": str(version.get("label", "")),
        "created_at": str(version.get("created_at", "")),
        "source": str(version.get("source", "")),
        "enabled_methods_total": len([item for item in methods if isinstance(item, dict) and bool(item.get("enabled", False))]),
        "enabled_controls_total": len([item for item in controls if isinstance(item, dict) and bool(item.get("enabled", False))]),
        "epochs_total": int(run_plan.get("epochs_total", 0) or 0) if isinstance(run_plan, dict) else 0,
    }


def _build_c5_launch_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Собирает публичную DTO запись launch history C5."""

    return {
        "run_id": str(entry.get("run_id", "")),
        "created_at": str(entry.get("created_at", "")),
        "status": str(entry.get("status", "")),
        "method_id": str(entry.get("method_id", "")),
        "epochs_total": int(entry.get("epochs_total", 0) or 0),
        "selected_candidates_total": int(entry.get("selected_candidates_total", 0) or 0),
        "assigned_datasets_total": int(entry.get("assigned_datasets_total", 0) or 0),
        "triggered_by": str(entry.get("triggered_by", "")),
    }


def _build_handler(*, project_root: Path, registry_store: WorkspaceRegistryStore) -> type[SimpleHTTPRequestHandler]:
    """Создает handler-класс с замыканием на project_root и registry_store."""

    class FrontendRequestHandler(SimpleHTTPRequestHandler):
        """HTTP handler для frontend shell: static + capability API + C1/C2 product API."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Инициализирует handler и настраивает root директорию раздачи статики."""

            super().__init__(*args, directory=str(project_root), **kwargs)

        def do_GET(self) -> None:  # noqa: N802
            """Обрабатывает GET-запросы API и static-файлов."""

            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            tenant_id, user_id = self._resolve_request_actor()
            if path == "/api/health":
                self._send_json({"status": "ok", "service": "frontend_dev_server"})
                return

            if path == "/api/capabilities":
                self._send_json(build_capability_catalog_payload())
                return

            if path == "/api/evaluation/evaluator-adapters":
                self._handle_get_evaluator_adapter_catalog()
                return

            if path in {"/api/c2/sample", "/api/c3/sample", "/api/c4/sample", "/api/c5/sample", "/api/c5s/sample", "/api/c6/sample", "/api/c7/sample", "/api/c8/sample"}:
                capability_id = path.split("/")[2]
                self._send_json(build_stub_capability_payload(capability_id))
                return

            if path in {"/api/arenas", "/api/workspaces"}:
                self._handle_list_arenas(tenant_id=tenant_id, user_id=user_id, legacy_workspace=(path == "/api/workspaces"))
                return

            arena_get_match = re.fullmatch(r"/api/arenas/([^/]+)", path)
            if arena_get_match is not None:
                arena_id = arena_get_match.group(1)
                self._handle_get_arena(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            arena_chat_state_match = re.fullmatch(r"/api/arenas/([^/]+)/chat/state", path)
            if arena_chat_state_match is not None:
                arena_id = arena_chat_state_match.group(1)
                self._handle_get_arena_chat_state(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            arena_pattern_selection_match = re.fullmatch(r"/api/arenas/([^/]+)/patterns/selection", path)
            if arena_pattern_selection_match is not None:
                arena_id = arena_pattern_selection_match.group(1)
                self._handle_get_arena_pattern_selection(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            arena_pattern_search_match = re.fullmatch(r"/api/arenas/([^/]+)/patterns/search", path)
            if arena_pattern_search_match is not None:
                arena_id = arena_pattern_search_match.group(1)
                self._handle_search_arena_patterns(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_id,
                    query_params=query_params,
                )
                return

            arena_datasets_state_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/state", path)
            if arena_datasets_state_match is not None:
                arena_id = arena_datasets_state_match.group(1)
                self._handle_get_arena_dataset_state(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            arena_evaluation_state_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/state", path)
            if arena_evaluation_state_match is not None:
                arena_id = arena_evaluation_state_match.group(1)
                self._handle_get_arena_evaluation_state(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            arena_stage_mapping_state_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/stage-mapping/state", path)
            if arena_stage_mapping_state_match is not None:
                arena_id = arena_stage_mapping_state_match.group(1)
                self._handle_get_arena_evaluation_stage_mapping_state(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            arena_optimizer_state_match = re.fullmatch(r"/api/arenas/([^/]+)/optimizer/state", path)
            if arena_optimizer_state_match is not None:
                arena_id = arena_optimizer_state_match.group(1)
                self._handle_get_arena_optimizer_state(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            # Русский комментарий: оставляем legacy project-роут как alias к arena id для плавной миграции.
            project_chat_state_match = re.fullmatch(r"/api/projects/([^/]+)/chat/state", path)
            if project_chat_state_match is not None:
                arena_id = project_chat_state_match.group(1)
                self._handle_get_arena_chat_state(tenant_id=tenant_id, user_id=user_id, arena_id=arena_id)
                return

            if self.path.startswith("/assets/"):
                dist_assets_path = project_root / "frontend" / "dist" / "assets"
                if dist_assets_path.exists():
                    self.path = f"/frontend/dist{self.path}"

            if self.path == "/" or self.path == "/index.html" or self.path.startswith("/battles"):
                dist_index_path = project_root / "frontend" / "dist" / "index.html"
                if dist_index_path.exists():
                    self.path = "/frontend/dist/index.html"
                else:
                    self.path = "/frontend/index.html"

            super().do_GET()

        def do_POST(self) -> None:  # noqa: N802
            """Обрабатывает POST-запросы API для C1/C2 и legacy debug endpoint."""

            path = urlparse(self.path).path
            tenant_id, user_id = self._resolve_request_actor()

            if path in {"/api/arenas", "/api/workspaces"}:
                self._handle_create_arena(tenant_id=tenant_id, user_id=user_id, legacy_workspace=(path == "/api/workspaces"))
                return

            arena_rename_match = re.fullmatch(r"/api/arenas/([^/]+)/rename", path)
            if arena_rename_match is not None:
                self._handle_rename_arena(tenant_id=tenant_id, user_id=user_id, arena_id=arena_rename_match.group(1), legacy_workspace=False)
                return

            arena_delete_match = re.fullmatch(r"/api/arenas/([^/]+)/delete", path)
            if arena_delete_match is not None:
                self._handle_delete_arena(tenant_id=tenant_id, user_id=user_id, arena_id=arena_delete_match.group(1), legacy_workspace=False)
                return

            arena_duplicate_match = re.fullmatch(r"/api/arenas/([^/]+)/duplicate", path)
            if arena_duplicate_match is not None:
                self._handle_duplicate_arena(tenant_id=tenant_id, user_id=user_id, arena_id=arena_duplicate_match.group(1), legacy_workspace=False)
                return

            workspace_rename_match = re.fullmatch(r"/api/workspaces/([^/]+)/rename", path)
            if workspace_rename_match is not None:
                self._handle_rename_arena(tenant_id=tenant_id, user_id=user_id, arena_id=workspace_rename_match.group(1), legacy_workspace=True)
                return

            workspace_delete_match = re.fullmatch(r"/api/workspaces/([^/]+)/delete", path)
            if workspace_delete_match is not None:
                self._handle_delete_arena(tenant_id=tenant_id, user_id=user_id, arena_id=workspace_delete_match.group(1), legacy_workspace=True)
                return

            workspace_duplicate_match = re.fullmatch(r"/api/workspaces/([^/]+)/duplicate", path)
            if workspace_duplicate_match is not None:
                self._handle_duplicate_arena(tenant_id=tenant_id, user_id=user_id, arena_id=workspace_duplicate_match.group(1), legacy_workspace=True)
                return

            arena_chat_match = re.fullmatch(r"/api/arenas/([^/]+)/chat/messages", path)
            if arena_chat_match is not None:
                self._handle_post_arena_chat_message(tenant_id=tenant_id, user_id=user_id, arena_id=arena_chat_match.group(1))
                return

            arena_compile_match = re.fullmatch(r"/api/arenas/([^/]+)/candidates/select-for-tests", path)
            if arena_compile_match is not None:
                self._handle_post_arena_candidates_select_for_tests(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_compile_match.group(1),
                )
                return

            arena_pattern_selection_match = re.fullmatch(r"/api/arenas/([^/]+)/patterns/selection", path)
            if arena_pattern_selection_match is not None:
                self._handle_post_arena_pattern_selection(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_pattern_selection_match.group(1),
                )
                return

            arena_dataset_create_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/create", path)
            if arena_dataset_create_match is not None:
                self._handle_post_arena_dataset_create(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_create_match.group(1),
                )
                return

            arena_dataset_select_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/select", path)
            if arena_dataset_select_match is not None:
                self._handle_post_arena_dataset_select(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_select_match.group(1),
                )
                return

            arena_dataset_assign_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/assign", path)
            if arena_dataset_assign_match is not None:
                self._handle_post_arena_dataset_assign(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_assign_match.group(1),
                )
                return

            arena_dataset_add_row_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/([^/]+)/rows/add", path)
            if arena_dataset_add_row_match is not None:
                self._handle_post_arena_dataset_row_add(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_add_row_match.group(1),
                    dataset_id=arena_dataset_add_row_match.group(2),
                )
                return

            arena_dataset_replace_rows_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/([^/]+)/rows/replace", path)
            if arena_dataset_replace_rows_match is not None:
                self._handle_post_arena_dataset_rows_replace(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_replace_rows_match.group(1),
                    dataset_id=arena_dataset_replace_rows_match.group(2),
                )
                return

            arena_dataset_validate_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/([^/]+)/validate", path)
            if arena_dataset_validate_match is not None:
                self._handle_post_arena_dataset_validate(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_validate_match.group(1),
                    dataset_id=arena_dataset_validate_match.group(2),
                )
                return

            arena_dataset_save_version_match = re.fullmatch(r"/api/arenas/([^/]+)/datasets/([^/]+)/save-version", path)
            if arena_dataset_save_version_match is not None:
                self._handle_post_arena_dataset_save_version(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_dataset_save_version_match.group(1),
                    dataset_id=arena_dataset_save_version_match.group(2),
                )
                return

            arena_evaluation_metrics_save_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/metrics/save", path)
            if arena_evaluation_metrics_save_match is not None:
                self._handle_post_arena_evaluation_metrics_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_metrics_save_match.group(1),
                )
                return

            arena_evaluation_evaluators_save_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/evaluators/save", path)
            if arena_evaluation_evaluators_save_match is not None:
                self._handle_post_arena_evaluation_evaluators_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_evaluators_save_match.group(1),
                )
                return

            arena_evaluation_matrix_save_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/matrix/save", path)
            if arena_evaluation_matrix_save_match is not None:
                self._handle_post_arena_evaluation_matrix_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_matrix_save_match.group(1),
                )
                return

            arena_evaluation_stage_bindings_save_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/stage-bindings/save", path)
            if arena_evaluation_stage_bindings_save_match is not None:
                self._handle_post_arena_evaluation_stage_bindings_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_stage_bindings_save_match.group(1),
                )
                return

            arena_evaluation_stage_bindings_suggest_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/stage-bindings/suggest", path)
            if arena_evaluation_stage_bindings_suggest_match is not None:
                self._handle_post_arena_evaluation_stage_bindings_suggest(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_stage_bindings_suggest_match.group(1),
                )
                return

            arena_evaluation_stage_mappings_save_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/stage-mapping/save", path)
            if arena_evaluation_stage_mappings_save_match is not None:
                self._handle_post_arena_evaluation_stage_mappings_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_stage_mappings_save_match.group(1),
                )
                return

            arena_evaluation_stage_mappings_auto_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/stage-mapping/auto-map", path)
            if arena_evaluation_stage_mappings_auto_match is not None:
                self._handle_post_arena_evaluation_stage_mappings_auto_map(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_stage_mappings_auto_match.group(1),
                )
                return

            arena_evaluation_budget_save_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/budget/save", path)
            if arena_evaluation_budget_save_match is not None:
                self._handle_post_arena_evaluation_budget_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_budget_save_match.group(1),
                )
                return

            arena_evaluation_validate_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/validate", path)
            if arena_evaluation_validate_match is not None:
                self._handle_post_arena_evaluation_validate(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_validate_match.group(1),
                )
                return

            arena_evaluation_save_version_match = re.fullmatch(r"/api/arenas/([^/]+)/evaluation/save-version", path)
            if arena_evaluation_save_version_match is not None:
                self._handle_post_arena_evaluation_save_version(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_evaluation_save_version_match.group(1),
                )
                return

            arena_optimizer_save_match = re.fullmatch(r"/api/arenas/([^/]+)/optimizer/save", path)
            if arena_optimizer_save_match is not None:
                self._handle_post_arena_optimizer_save(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_optimizer_save_match.group(1),
                )
                return

            arena_optimizer_validate_match = re.fullmatch(r"/api/arenas/([^/]+)/optimizer/validate", path)
            if arena_optimizer_validate_match is not None:
                self._handle_post_arena_optimizer_validate(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_optimizer_validate_match.group(1),
                )
                return

            arena_optimizer_save_version_match = re.fullmatch(r"/api/arenas/([^/]+)/optimizer/save-version", path)
            if arena_optimizer_save_version_match is not None:
                self._handle_post_arena_optimizer_save_version(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_optimizer_save_version_match.group(1),
                )
                return

            arena_optimizer_launch_match = re.fullmatch(r"/api/arenas/([^/]+)/optimizer/launch", path)
            if arena_optimizer_launch_match is not None:
                self._handle_post_arena_optimizer_launch(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_optimizer_launch_match.group(1),
                )
                return

            # Русский комментарий: legacy project-роут как alias к arena id для плавной миграции.
            project_chat_match = re.fullmatch(r"/api/projects/([^/]+)/chat/messages", path)
            if project_chat_match is not None:
                self._handle_post_arena_chat_message(tenant_id=tenant_id, user_id=user_id, arena_id=project_chat_match.group(1))
                return

            if path == "/api/c1/validate-compile":
                self._handle_legacy_validate_compile()
                return

            self._send_json({"status": "error", "message": "Not found"}, status=HTTPStatus.NOT_FOUND)

        def _handle_list_arenas(self, *, tenant_id: str, user_id: str, legacy_workspace: bool) -> None:
            """Возвращает tenant-scoped список арен с опциональным legacy-полем workspace."""

            arenas = [record.__dict__ for record in registry_store.list_arenas(tenant_id=tenant_id, owner_user_id=user_id)]
            payload = {
                "status": "success",
                "tenant_id": tenant_id,
                "owner_user_id": user_id,
                "arenas": arenas,
                "total": len(arenas),
            }
            if legacy_workspace:
                payload["workspaces"] = arenas
            self._send_json(payload)

        def _handle_get_arena(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает арену по идентификатору."""

            try:
                arena = registry_store.get_arena(tenant_id=tenant_id, owner_user_id=user_id, arena_id=arena_id)
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            self._send_json({"status": "success", "arena": arena.__dict__})

        def _handle_create_arena(self, *, tenant_id: str, user_id: str, legacy_workspace: bool) -> None:
            """Создает новую арену и возвращает созданную сущность."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            name = payload.get("name")
            description = payload.get("description", "")
            if not isinstance(name, str) or not name.strip():
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `name` must be a non-empty string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if not isinstance(description, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `description` must be a string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                arena = registry_store.create_arena(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    name=name,
                    description=description,
                )
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_conflict", "message": str(exc)},
                    status=HTTPStatus.CONFLICT,
                )
                return

            response_payload = {"status": "success", "arena": arena.__dict__}
            if legacy_workspace:
                response_payload["workspace"] = arena.__dict__
            self._send_json(response_payload, status=HTTPStatus.CREATED)

        def _handle_rename_arena(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            legacy_workspace: bool,
        ) -> None:
            """Переименовывает арену и возвращает обновленную запись."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            name = payload.get("name")
            if not isinstance(name, str) or not name.strip():
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `name` must be a non-empty string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                arena = registry_store.rename_arena(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    name=name,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_conflict", "message": str(exc)},
                    status=HTTPStatus.CONFLICT,
                )
                return

            response_payload = {"status": "success", "arena": arena.__dict__}
            if legacy_workspace:
                response_payload["workspace"] = arena.__dict__
            self._send_json(response_payload)

        def _handle_duplicate_arena(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            legacy_workspace: bool,
        ) -> None:
            """Дублирует арену и возвращает новую запись."""

            try:
                payload = self._read_json_body()
            except ValueError:
                payload = {}

            name_raw = payload.get("name")
            if name_raw is not None and not isinstance(name_raw, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `name` must be a string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                arena = registry_store.duplicate_arena(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    name=name_raw,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_conflict", "message": str(exc)},
                    status=HTTPStatus.CONFLICT,
                )
                return

            response_payload = {"status": "success", "arena": arena.__dict__}
            if legacy_workspace:
                response_payload["workspace"] = arena.__dict__
            self._send_json(response_payload, status=HTTPStatus.CREATED)

        def _handle_delete_arena(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            legacy_workspace: bool,
        ) -> None:
            """Удаляет арену в tenant/user scope."""

            try:
                registry_store.delete_arena(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            payload = {"status": "success", "arena_id": arena_id}
            if legacy_workspace:
                payload["workspace_id"] = arena_id
            self._send_json(payload)

        def _handle_get_arena_chat_state(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает состояние C2-чата и candidate draft для выбранной арены."""

            try:
                arena = registry_store.get_arena(tenant_id=tenant_id, owner_user_id=user_id, arena_id=arena_id)
                messages = registry_store.list_arena_chat_messages(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                candidate_set_draft = registry_store.get_arena_candidate_set_draft(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c2",
                    "arena_id": arena_id,
                    "arena_name": arena.name,
                    "messages": messages,
                    "messages_total": len(messages),
                    "candidate_set_draft": candidate_set_draft,
                }
            )

        def _handle_get_arena_pattern_selection(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает include/exclude выборку паттернов C3 для текущей арены."""

            try:
                selection = registry_store.get_arena_pattern_selection(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "selection_corrupted", "message": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c3",
                    "arena_id": arena_id,
                    "selection": selection,
                }
            )

        def _handle_search_arena_patterns(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            query_params: dict[str, list[str]],
        ) -> None:
            """Выполняет поиск паттернов C3 с retrieval trace в контексте текущей selection."""

            query = str((query_params.get("q", [""])[0] or "")).strip()
            limit_raw = str((query_params.get("limit", ["12"])[0] or "12")).strip()
            try:
                limit = int(limit_raw)
            except ValueError:
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Query param `limit` must be an integer."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                selection = registry_store.get_arena_pattern_selection(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                search_payload = search_pattern_library(
                    query=query,
                    limit=limit,
                    include_pattern_ids=selection.get("include_pattern_ids", []),
                    exclude_pattern_ids=selection.get("exclude_pattern_ids", []),
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c3",
                    "arena_id": arena_id,
                    "selection": selection,
                    **search_payload,
                }
            )

        def _handle_post_arena_chat_message(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Добавляет сообщение в C2-чат арены и опционально генерирует candidate draft."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            message_raw = payload.get("message")
            if not isinstance(message_raw, str) or not message_raw.strip():
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `message` must be a non-empty string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            generate_candidates = bool(payload.get("generate_candidates", False))
            max_candidates_raw = payload.get("max_candidates", 3)
            capability_id_raw = str(payload.get("capability_id", "c2")).strip().lower() or "c2"
            context_action_raw = str(payload.get("context_action", "")).strip().lower()
            if not isinstance(max_candidates_raw, int):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `max_candidates` must be an integer."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if max_candidates_raw < 1 or max_candidates_raw > 5:
                self._send_json(
                    {
                        "status": "error",
                        "code": "validation_error",
                        "message": "Field `max_candidates` must be between 1 and 5.",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if capability_id_raw not in {"c2", "c4", "c5", "c5s", "c6", "c7"}:
                self._send_json(
                    {
                        "status": "error",
                        "code": "validation_error",
                        "message": "Field `capability_id` must be one of: c2, c4, c5, c5s, c6, c7.",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                chat_message = registry_store.append_arena_chat_message(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    role="user",
                    content=message_raw,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            if capability_id_raw != "c2":
                contextual_payload = self._run_contextual_copilot_action(
                    registry_store=registry_store,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    arena_id=arena_id,
                    capability_id=capability_id_raw,
                    user_message=message_raw,
                    context_action=context_action_raw,
                )
                assistant_message = registry_store.append_arena_chat_message(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    role="assistant",
                    content=str(contextual_payload.get("assistant_text", "Context action completed.")),
                )
                messages = registry_store.list_arena_chat_messages(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                self._send_json(
                    {
                        "status": "success",
                        "capability_id": capability_id_raw,
                        "arena_id": arena_id,
                        "message": chat_message,
                        "assistant_message": assistant_message,
                        "messages": messages,
                        "messages_total": len(messages),
                        "copilot_context": {
                            "resolved_action": str(contextual_payload.get("resolved_action", "none")),
                            "allowed_actions": list(contextual_payload.get("allowed_actions", [])),
                            "summary": str(contextual_payload.get("summary", "")),
                        },
                    },
                    status=HTTPStatus.CREATED,
                )
                return

            candidate_set_draft: dict[str, Any] | None = None
            assistant_message: dict[str, Any] | None = None
            if generate_candidates:
                try:
                    selection = registry_store.get_arena_pattern_selection(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    candidate_set_draft = build_candidate_draft_from_brief(
                        arena_id=arena_id,
                        brief=message_raw,
                        max_candidates=max_candidates_raw,
                        preferred_pattern_refs=selection.get("include_pattern_ids", []),
                        excluded_pattern_refs=selection.get("exclude_pattern_ids", []),
                    )
                    registry_store.save_arena_candidate_set_draft(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                        candidate_set_draft=candidate_set_draft,
                    )
                    assistant_message = registry_store.append_arena_chat_message(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                        role="assistant",
                        content=f"Prepared {candidate_set_draft['total']} candidate drafts from the brief.",
                    )
                except ValueError as exc:
                    self._send_json(
                        {"status": "error", "code": "validation_error", "message": str(exc)},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
                except KeyError as exc:
                    self._send_json(
                        {"status": "error", "code": "arena_not_found", "message": str(exc)},
                        status=HTTPStatus.NOT_FOUND,
                    )
                    return

            messages = registry_store.list_arena_chat_messages(
                tenant_id=tenant_id,
                owner_user_id=user_id,
                arena_id=arena_id,
            )
            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c2",
                    "arena_id": arena_id,
                    "message": chat_message,
                    "assistant_message": assistant_message,
                    "messages": messages,
                    "messages_total": len(messages),
                    "candidate_set_draft": candidate_set_draft,
                },
                status=HTTPStatus.CREATED,
            )

        def _run_contextual_copilot_action(
            self,
            *,
            registry_store: WorkspaceRegistryStore,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            capability_id: str,
            user_message: str,
            context_action: str,
        ) -> dict[str, Any]:
            """Выполняет tab-scoped copilot действие для выбранной capability."""

            normalized_message = user_message.strip().lower()
            if capability_id == "c4":
                allowed_actions = ["add_dataset_row"]
                resolved_action = context_action if context_action in allowed_actions else ""
                if not resolved_action and ("add row" in normalized_message or "добав" in normalized_message):
                    resolved_action = "add_dataset_row"
                if resolved_action == "add_dataset_row":
                    dataset_state = registry_store.get_arena_dataset_studio_state(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    active_dataset_id = str(dataset_state.get("active_dataset_id", ""))
                    if not active_dataset_id:
                        return {
                            "assistant_text": "No active dataset. Open Datasets and select one dataset first.",
                            "resolved_action": "add_dataset_row",
                            "allowed_actions": allowed_actions,
                            "summary": "Dataset row was not added.",
                        }
                    case_id = f"case_{uuid4().hex[:8]}"
                    registry_store.append_arena_dataset_row(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                        dataset_id=active_dataset_id,
                        row={
                            "case_id": case_id,
                            "input": "Synthetic input draft from copilot.",
                            "target_stage": "final",
                            "expected_payload": {"answer": "Synthetic expected answer draft."},
                            "expected": "Synthetic expected answer draft.",
                            "notes": "copilot:add_dataset_row",
                        },
                    )
                    return {
                        "assistant_text": f"Added dataset row `{case_id}` to active dataset `{active_dataset_id}`.",
                        "resolved_action": "add_dataset_row",
                        "allowed_actions": allowed_actions,
                        "summary": "Dataset row added.",
                    }
                return {
                    "assistant_text": "Datasets copilot is active. Try: 'add row'.",
                    "resolved_action": "none",
                    "allowed_actions": allowed_actions,
                    "summary": "No dataset action executed.",
                }

            if capability_id == "c5":
                allowed_actions = ["enable_default_metrics"]
                resolved_action = context_action if context_action in allowed_actions else ""
                if not resolved_action and ("enable metrics" in normalized_message or "включи метрики" in normalized_message):
                    resolved_action = "enable_default_metrics"
                if resolved_action == "enable_default_metrics":
                    evaluation_state = registry_store.get_arena_evaluation_studio_state(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    comparative: list[dict[str, Any]] = []
                    for item in evaluation_state.get("comparative_metrics", []):
                        if not isinstance(item, dict):
                            continue
                        metric = dict(item)
                        if str(metric.get("availability_status", "available")) != "unavailable":
                            metric["enabled"] = True
                        comparative.append(metric)
                    diagnostic: list[dict[str, Any]] = []
                    for item in evaluation_state.get("diagnostic_signals", []):
                        if not isinstance(item, dict):
                            continue
                        signal = dict(item)
                        if str(signal.get("availability_status", "available")) != "unavailable":
                            signal["enabled"] = True
                        diagnostic.append(signal)
                    registry_store.save_arena_evaluation_metrics(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                        comparative_metrics=comparative,
                        diagnostic_signals=diagnostic,
                    )
                    return {
                        "assistant_text": "Enabled available metrics/signals. Review weights in Metrics.",
                        "resolved_action": "enable_default_metrics",
                        "allowed_actions": allowed_actions,
                        "summary": "Metrics were updated.",
                    }
                return {
                    "assistant_text": "Metrics copilot is active. Try: 'enable metrics'.",
                    "resolved_action": "none",
                    "allowed_actions": allowed_actions,
                    "summary": "No metrics action executed.",
                }

            if capability_id == "c5s":
                allowed_actions = ["auto_map_stage_mappings", "add_mapping_row"]
                resolved_action = context_action if context_action in allowed_actions else ""
                if not resolved_action and ("auto map" in normalized_message or "automap" in normalized_message):
                    resolved_action = "auto_map_stage_mappings"
                if not resolved_action and ("add mapping" in normalized_message or "add row" in normalized_message or "добав" in normalized_message):
                    resolved_action = "add_mapping_row"
                if resolved_action == "auto_map_stage_mappings":
                    payload = registry_store.auto_map_arena_evaluation_stage_mappings(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    stage_mappings = payload.get("stage_mappings", [])
                    if isinstance(stage_mappings, list) and stage_mappings:
                        registry_store.save_arena_evaluation_stage_mappings(
                            tenant_id=tenant_id,
                            owner_user_id=user_id,
                            arena_id=arena_id,
                            stage_mappings=[dict(item) for item in stage_mappings if isinstance(item, dict)],
                        )
                        return {
                            "assistant_text": f"Auto-mapped and saved {len(stage_mappings)} stage mapping row(s).",
                            "resolved_action": "auto_map_stage_mappings",
                            "allowed_actions": allowed_actions,
                            "summary": "Stage mappings auto-initialized.",
                        }
                    return {
                        "assistant_text": "Auto-map found no rows. Add mapping row manually.",
                        "resolved_action": "auto_map_stage_mappings",
                        "allowed_actions": allowed_actions,
                        "summary": "No stage mapping suggestions.",
                    }
                if resolved_action == "add_mapping_row":
                    candidate_set = registry_store.get_arena_candidate_set_draft(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    first_candidate: dict[str, Any] | None = None
                    if isinstance(candidate_set, dict):
                        candidates = candidate_set.get("candidates", [])
                        if isinstance(candidates, list):
                            first_candidate = next((item for item in candidates if isinstance(item, dict)), None)
                    candidate_id = str((first_candidate or {}).get("candidate_id", ""))
                    candidate_title = str((first_candidate or {}).get("title", "Select candidate"))
                    evaluation_state = registry_store.get_arena_evaluation_studio_state(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    stage_mappings = [dict(item) for item in evaluation_state.get("stage_mappings", []) if isinstance(item, dict)]
                    stage_mappings.append(
                        {
                            "mapping_id": f"map_manual_{uuid4().hex[:8]}",
                            "target_stage": "retrieval",
                            "candidate_id": candidate_id,
                            "candidate_title": candidate_title,
                            "selected_node_ids": [],
                            "suggested_node_ids": [],
                            "status": "missing",
                            "confidence": 0.0,
                            "reason": "manual_row_created",
                            "enabled": True,
                            "notes": "copilot:add_mapping_row",
                            "source": "manual",
                        }
                    )
                    registry_store.save_arena_evaluation_stage_mappings(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                        stage_mappings=stage_mappings,
                    )
                    return {
                        "assistant_text": "Added one manual stage mapping row. Fill candidate and node ids.",
                        "resolved_action": "add_mapping_row",
                        "allowed_actions": allowed_actions,
                        "summary": "Manual stage mapping row added.",
                    }
                return {
                    "assistant_text": "Stage Mapping copilot is active. Try: 'auto map' or 'add mapping row'.",
                    "resolved_action": "none",
                    "allowed_actions": allowed_actions,
                    "summary": "No stage mapping action executed.",
                }

            if capability_id == "c6":
                allowed_actions = ["autofill_matrix_links"]
                resolved_action = context_action if context_action in allowed_actions else ""
                if not resolved_action and ("autofill" in normalized_message or "fill matrix" in normalized_message or "заполни матрицу" in normalized_message):
                    resolved_action = "autofill_matrix_links"
                if resolved_action == "autofill_matrix_links":
                    evaluation_state = registry_store.get_arena_evaluation_studio_state(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    enabled_evaluators = [item for item in evaluation_state.get("evaluators", []) if isinstance(item, dict) and bool(item.get("enabled", False))]
                    links: list[dict[str, Any]] = []
                    for metric in evaluation_state.get("comparative_metrics", []):
                        if not isinstance(metric, dict):
                            continue
                        if not bool(metric.get("enabled", False)) or str(metric.get("availability_status", "available")) == "unavailable":
                            continue
                        metric_id = str(metric.get("metric_id", ""))
                        for evaluator in enabled_evaluators:
                            links.append(
                                {
                                    "evaluator_id": str(evaluator.get("evaluator_id", "")),
                                    "metric_kind": "comparative",
                                    "metric_id": metric_id,
                                    "enabled": True,
                                }
                            )
                    for signal in evaluation_state.get("diagnostic_signals", []):
                        if not isinstance(signal, dict):
                            continue
                        if not bool(signal.get("enabled", False)) or str(signal.get("availability_status", "available")) == "unavailable":
                            continue
                        signal_id = str(signal.get("signal_id", ""))
                        for evaluator in enabled_evaluators:
                            links.append(
                                {
                                    "evaluator_id": str(evaluator.get("evaluator_id", "")),
                                    "metric_kind": "diagnostic",
                                    "metric_id": signal_id,
                                    "enabled": True,
                                }
                            )
                    saved_state = registry_store.save_arena_evaluation_evaluator_metric_links(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                        evaluator_metric_links=links,
                    )
                    saved_links = [
                        item
                        for item in saved_state.get("evaluator_metric_links", [])
                        if isinstance(item, dict)
                    ]
                    enabled_links_total = sum(1 for item in saved_links if bool(item.get("enabled", False)))
                    unsupported_links_total = sum(
                        1 for item in saved_links if str(item.get("compatibility_status", "compatible")) == "incompatible"
                    )
                    return {
                        "assistant_text": (
                            f"Autofilled {enabled_links_total} compatible link(s); "
                            f"skipped {unsupported_links_total} unsupported link(s)."
                        ),
                        "resolved_action": "autofill_matrix_links",
                        "allowed_actions": allowed_actions,
                        "summary": "Evaluator matrix links updated with compatibility guard.",
                    }
                return {
                    "assistant_text": "Evaluators copilot is active. Try: 'autofill matrix'.",
                    "resolved_action": "none",
                    "allowed_actions": allowed_actions,
                    "summary": "No evaluator action executed.",
                }

            if capability_id == "c7":
                allowed_actions = ["validate_optimizer_setup"]
                resolved_action = context_action if context_action in allowed_actions else ""
                if not resolved_action and ("validate" in normalized_message or "проверь" in normalized_message):
                    resolved_action = "validate_optimizer_setup"
                if resolved_action == "validate_optimizer_setup":
                    report = registry_store.validate_arena_optimizer_setup(
                        tenant_id=tenant_id,
                        owner_user_id=user_id,
                        arena_id=arena_id,
                    )
                    issues = report.get("issues", [])
                    if not isinstance(issues, list):
                        issues = []
                    if issues:
                        top_issue = issues[0] if isinstance(issues[0], dict) else {}
                        top_message = str(top_issue.get("message", "unknown issue"))
                        return {
                            "assistant_text": f"Optimizer preflight: {report.get('status', 'unknown')}. Top issue: {top_message}",
                            "resolved_action": "validate_optimizer_setup",
                            "allowed_actions": allowed_actions,
                            "summary": f"Validation returned {len(issues)} issue(s).",
                        }
                    return {
                        "assistant_text": "Optimizer preflight is ready.",
                        "resolved_action": "validate_optimizer_setup",
                        "allowed_actions": allowed_actions,
                        "summary": "Optimizer validation passed.",
                    }
                return {
                    "assistant_text": "Optimizer copilot is active. Try: 'validate optimizer'.",
                    "resolved_action": "none",
                    "allowed_actions": allowed_actions,
                    "summary": "No optimizer action executed.",
                }

            return {
                "assistant_text": "Context action is not available for this capability.",
                "resolved_action": "none",
                "allowed_actions": [],
                "summary": "No contextual action executed.",
            }

        def _handle_post_arena_candidates_select_for_tests(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Отмечает выбранных кандидатов и внутренне готовит их к тестам (compile gate без ручного шага)."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            selected_candidate_ids_raw = payload.get("candidate_ids", [])
            if not isinstance(selected_candidate_ids_raw, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `candidate_ids` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            selected_candidate_ids = [str(item).strip() for item in selected_candidate_ids_raw]
            max_compile_attempts_raw = payload.get("max_compile_attempts", 3)
            if not isinstance(max_compile_attempts_raw, int):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `max_compile_attempts` must be an integer."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                candidate_set_draft = registry_store.get_arena_candidate_set_draft(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            if candidate_set_draft is None:
                self._send_json(
                    {
                        "status": "error",
                        "code": "candidate_draft_missing",
                        "message": "Candidate draft is empty. Generate candidates first.",
                    },
                    status=HTTPStatus.CONFLICT,
                )
                return

            try:
                compiled_draft = select_candidates_for_tests_and_prepare(
                    candidate_set_draft=candidate_set_draft,
                    selected_candidate_ids=selected_candidate_ids,
                    project_root=project_root,
                    max_compile_attempts=max_compile_attempts_raw,
                )
                registry_store.save_arena_candidate_set_draft(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    candidate_set_draft=compiled_draft,
                )
                compile_gate = compiled_draft.get("compile_gate", {})
                assistant_message = registry_store.append_arena_chat_message(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    role="assistant",
                    content=(
                        "Candidates selected for tests: "
                        f"{compile_gate.get('selected_candidates', 0)} selected, "
                        f"{compile_gate.get('ready_candidates', 0)} prepared, "
                        f"{compile_gate.get('failed_candidates', 0)} issue(s)."
                    ),
                )
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            messages = registry_store.list_arena_chat_messages(
                tenant_id=tenant_id,
                owner_user_id=user_id,
                arena_id=arena_id,
            )
            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c2",
                    "action": "select_candidates_for_tests",
                    "arena_id": arena_id,
                    "assistant_message": assistant_message,
                    "messages": messages,
                    "messages_total": len(messages),
                    "candidate_set_draft": compiled_draft,
                    "compile_gate": compiled_draft.get("compile_gate", {}),
                }
            )

        def _handle_post_arena_pattern_selection(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Обновляет include/exclude выборку паттернов C3 для арены."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            include_pattern_ids = payload.get("include_pattern_ids", [])
            exclude_pattern_ids = payload.get("exclude_pattern_ids", [])
            if not isinstance(include_pattern_ids, list) or not isinstance(exclude_pattern_ids, list):
                self._send_json(
                    {
                        "status": "error",
                        "code": "validation_error",
                        "message": "Fields `include_pattern_ids` and `exclude_pattern_ids` must be arrays.",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                selection = registry_store.save_arena_pattern_selection(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    include_pattern_ids=include_pattern_ids,
                    exclude_pattern_ids=exclude_pattern_ids,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as exc:
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c3",
                    "arena_id": arena_id,
                    "selection": selection,
                }
            )

        def _handle_get_arena_dataset_state(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает состояние C4 Dataset Studio для выбранной арены."""

            try:
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(_build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state))

        def _handle_post_arena_dataset_create(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Создает dataset в C4 Studio и возвращает обновленное состояние."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            name = payload.get("name", "")
            description = payload.get("description", "")
            if not isinstance(name, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `name` must be a string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if not isinstance(description, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `description` must be a string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                dataset = registry_store.create_arena_dataset(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    name=name,
                    description=description,
                )
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "create_dataset"
            response_payload["dataset"] = _build_c4_dataset_detail(dataset)
            self._send_json(response_payload, status=HTTPStatus.CREATED)

        def _handle_post_arena_dataset_select(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Устанавливает активный dataset в C4 Studio."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            dataset_id = payload.get("dataset_id")
            if not isinstance(dataset_id, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `dataset_id` must be a string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                registry_store.set_active_arena_dataset(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    dataset_id=dataset_id,
                )
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "select_dataset"
            self._send_json(response_payload)

        def _handle_post_arena_dataset_row_add(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            dataset_id: str,
        ) -> None:
            """Добавляет одну row в dataset C4 Studio."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            row_raw = payload.get("row")
            if not isinstance(row_raw, dict):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `row` must be an object."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                row = registry_store.append_arena_dataset_row(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    dataset_id=dataset_id,
                    row=row_raw,
                )
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "add_row"
            response_payload["row"] = row
            self._send_json(response_payload)

        def _handle_post_arena_dataset_assign(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет выбранные пользователем dataset-ы для прогона арены."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            dataset_ids_raw = payload.get("dataset_ids", [])
            if not isinstance(dataset_ids_raw, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `dataset_ids` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, str) for item in dataset_ids_raw):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Dataset ids must contain strings only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_assigned_datasets(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    dataset_ids=[str(item) for item in dataset_ids_raw],
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "assign_datasets"
            self._send_json(response_payload)

        def _handle_post_arena_dataset_rows_replace(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            dataset_id: str,
        ) -> None:
            """Заменяет все rows dataset в C4 Studio."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            rows_raw = payload.get("rows")
            if not isinstance(rows_raw, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `rows` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            row_items = [item for item in rows_raw if isinstance(item, dict)]
            if len(row_items) != len(rows_raw):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Dataset rows must contain objects only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                dataset = registry_store.replace_arena_dataset_rows(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    dataset_id=dataset_id,
                    rows=row_items,
                )
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "replace_rows"
            response_payload["dataset"] = _build_c4_dataset_detail(dataset)
            self._send_json(response_payload)

        def _handle_post_arena_dataset_validate(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            dataset_id: str,
        ) -> None:
            """Выполняет базовую проверку dataset и возвращает issues-репорт."""

            try:
                validation_report = registry_store.validate_arena_dataset(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    dataset_id=dataset_id,
                )
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "validate_dataset"
            response_payload["validation_report"] = validation_report
            self._send_json(response_payload)

        def _handle_post_arena_dataset_save_version(
            self,
            *,
            tenant_id: str,
            user_id: str,
            arena_id: str,
            dataset_id: str,
        ) -> None:
            """Сохраняет snapshot-версию dataset в C4 Studio."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            label = payload.get("label", "")
            source = payload.get("source", "manual")
            if not isinstance(label, str) or not isinstance(source, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Fields `label` and `source` must be strings."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                version = registry_store.save_arena_dataset_version(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    dataset_id=dataset_id,
                    label=label,
                    source=source,
                )
                studio_state = registry_store.get_arena_dataset_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                code = "arena_not_found" if "Workspace not found" in str(exc) else "dataset_not_found"
                self._send_json({"status": "error", "code": code, "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_dataset_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_dataset_version"
            response_payload["version"] = _build_c4_dataset_version(version)
            self._send_json(response_payload)

        def _handle_get_arena_evaluation_state(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает состояние C4 Metrics & Evaluators Studio для выбранной арены."""

            try:
                studio_state = registry_store.get_arena_evaluation_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(_build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state))

        def _handle_get_evaluator_adapter_catalog(self) -> None:
            """Возвращает catalog evaluator-adapters для C6 и developer docs."""

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c6",
                    "adapters": registry_store.get_evaluator_adapter_catalog(),
                }
            )

        def _handle_get_arena_evaluation_stage_mapping_state(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает только stage mapping часть состояния C4 evaluation."""

            try:
                studio_state = registry_store.get_arena_evaluation_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c4",
                    "arena_id": arena_id,
                    "stage_mappings": [dict(item) for item in studio_state.get("stage_mappings", []) if isinstance(item, dict)],
                    "stage_mapping_coverage": [
                        dict(item) for item in studio_state.get("stage_mapping_coverage", []) if isinstance(item, dict)
                    ],
                    "updated_at": str(studio_state.get("updated_at", "")),
                }
            )

        def _handle_post_arena_evaluation_metrics_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет comparative/diagnostic метрики evaluation profile."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            comparative_metrics = payload.get("comparative_metrics", [])
            diagnostic_signals = payload.get("diagnostic_signals", [])
            if not isinstance(comparative_metrics, list) or not isinstance(diagnostic_signals, list):
                self._send_json(
                    {
                        "status": "error",
                        "code": "validation_error",
                        "message": "Fields `comparative_metrics` and `diagnostic_signals` must be arrays.",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, dict) for item in comparative_metrics) or any(not isinstance(item, dict) for item in diagnostic_signals):
                self._send_json(
                    {
                        "status": "error",
                        "code": "validation_error",
                        "message": "Metrics payload must contain objects only.",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_evaluation_metrics(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    comparative_metrics=[dict(item) for item in comparative_metrics],
                    diagnostic_signals=[dict(item) for item in diagnostic_signals],
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_evaluation_metrics"
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_evaluators_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет evaluator-адаптеры evaluation profile."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            evaluators = payload.get("evaluators", [])
            if not isinstance(evaluators, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `evaluators` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, dict) for item in evaluators):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `evaluators` must contain objects only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_evaluation_evaluators(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    evaluators=[dict(item) for item in evaluators],
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_evaluation_evaluators"
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_matrix_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет матрицу покрытия Evaluator x Metric для evaluation profile."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            evaluator_metric_links = payload.get("evaluator_metric_links", [])
            if not isinstance(evaluator_metric_links, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `evaluator_metric_links` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, dict) for item in evaluator_metric_links):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `evaluator_metric_links` must contain objects only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_evaluation_evaluator_metric_links(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    evaluator_metric_links=[dict(item) for item in evaluator_metric_links],
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_evaluation_matrix"
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_stage_bindings_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет stage_ref bindings для non-final stage-оценки."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            stage_bindings = payload.get("stage_bindings", [])
            if not isinstance(stage_bindings, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `stage_bindings` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, dict) for item in stage_bindings):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `stage_bindings` must contain objects only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_evaluation_stage_bindings(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    stage_bindings=[dict(item) for item in stage_bindings],
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_stage_bindings"
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_stage_bindings_suggest(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает предложенные stage_ref bindings без автосохранения профиля."""

            try:
                suggestion_payload = registry_store.suggest_arena_evaluation_stage_bindings(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                studio_state = registry_store.get_arena_evaluation_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "suggest_stage_bindings"
            response_payload["suggested_stage_bindings"] = [dict(item) for item in suggestion_payload.get("stage_bindings", []) if isinstance(item, dict)]
            response_payload["suggested_stage_binding_coverage"] = [
                dict(item) for item in suggestion_payload.get("stage_binding_coverage", []) if isinstance(item, dict)
            ]
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_stage_mappings_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет stage mappings (target_stage -> candidate nodes) для non-final оценки."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            stage_mappings = payload.get("stage_mappings", [])
            if not isinstance(stage_mappings, list):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `stage_mappings` must be an array."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, dict) for item in stage_mappings):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `stage_mappings` must contain objects only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_evaluation_stage_mappings(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    stage_mappings=[dict(item) for item in stage_mappings],
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_stage_mappings"
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_stage_mappings_auto_map(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает auto-map stage mappings без сохранения в профиль."""

            try:
                suggestion_payload = registry_store.auto_map_arena_evaluation_stage_mappings(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                studio_state = registry_store.get_arena_evaluation_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "auto_map_stage_mappings"
            response_payload["suggested_stage_mappings"] = [dict(item) for item in suggestion_payload.get("stage_mappings", []) if isinstance(item, dict)]
            response_payload["suggested_stage_mapping_coverage"] = [
                dict(item) for item in suggestion_payload.get("stage_mapping_coverage", []) if isinstance(item, dict)
            ]
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_budget_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет бюджетные ограничения evaluation profile."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            budget = payload.get("budget", {})
            if not isinstance(budget, dict):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `budget` must be an object."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_evaluation_budget(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    budget=budget,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_evaluation_budget"
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_validate(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Валидирует текущий evaluation profile и возвращает issues-отчет."""

            try:
                validation_report = registry_store.validate_arena_evaluation_profile(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                studio_state = registry_store.get_arena_evaluation_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "validate_evaluation_profile"
            response_payload["validation_report"] = validation_report
            self._send_json(response_payload)

        def _handle_post_arena_evaluation_save_version(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет snapshot-версию evaluation profile."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            label = payload.get("label", "")
            source = payload.get("source", "manual")
            if not isinstance(label, str) or not isinstance(source, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Fields `label` and `source` must be strings."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                version = registry_store.save_arena_evaluation_version(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    label=label,
                    source=source,
                )
                studio_state = registry_store.get_arena_evaluation_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return

            response_payload = _build_c4_evaluation_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_evaluation_version"
            response_payload["version"] = _build_c4_evaluation_version(version)
            self._send_json(response_payload)

        def _handle_get_arena_optimizer_state(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Возвращает состояние C5 Optimizer Setup Studio для выбранной арены."""

            try:
                studio_state = registry_store.get_arena_optimizer_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json(
                    {"status": "error", "code": "arena_not_found", "message": str(exc)},
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(_build_c5_optimizer_state_payload(arena_id=arena_id, studio_state=studio_state))

        def _handle_post_arena_optimizer_save(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет C5 optimizer setup (methods/controls/run_plan/budget)."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            methods = payload.get("methods", [])
            controls = payload.get("controls", [])
            run_plan = payload.get("run_plan", {})
            budget = payload.get("budget", {})
            if not isinstance(methods, list) or not isinstance(controls, list) or not isinstance(run_plan, dict) or not isinstance(budget, dict):
                self._send_json(
                    {
                        "status": "error",
                        "code": "validation_error",
                        "message": "Fields `methods`/`controls` must be arrays and `run_plan`/`budget` must be objects.",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if any(not isinstance(item, dict) for item in methods) or any(not isinstance(item, dict) for item in controls):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Methods and controls must contain objects only."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                studio_state = registry_store.save_arena_optimizer_setup(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    methods=[dict(item) for item in methods],
                    controls=[dict(item) for item in controls],
                    run_plan=dict(run_plan),
                    budget=dict(budget),
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c5_optimizer_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_optimizer_setup"
            self._send_json(response_payload)

        def _handle_post_arena_optimizer_validate(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Валидирует C5 optimizer setup и возвращает guardrail-issues."""

            try:
                validation_report = registry_store.validate_arena_optimizer_setup(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                studio_state = registry_store.get_arena_optimizer_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return

            response_payload = _build_c5_optimizer_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "validate_optimizer_setup"
            response_payload["validation_report"] = validation_report
            self._send_json(response_payload)

        def _handle_post_arena_optimizer_save_version(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Сохраняет snapshot-версию C5 optimizer setup."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            label = payload.get("label", "")
            source = payload.get("source", "manual")
            if not isinstance(label, str) or not isinstance(source, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Fields `label` and `source` must be strings."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                version = registry_store.save_arena_optimizer_version(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    label=label,
                    source=source,
                )
                studio_state = registry_store.get_arena_optimizer_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._send_json({"status": "error", "code": "validation_error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            response_payload = _build_c5_optimizer_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "save_optimizer_version"
            response_payload["version"] = _build_c5_optimizer_version(version)
            self._send_json(response_payload)

        def _handle_post_arena_optimizer_launch(self, *, tenant_id: str, user_id: str, arena_id: str) -> None:
            """Запускает C5 optimizer run с preflight-guardrails."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            triggered_by = payload.get("triggered_by", "manual")
            if not isinstance(triggered_by, str):
                self._send_json(
                    {"status": "error", "code": "validation_error", "message": "Field `triggered_by` must be a string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                run_entry = registry_store.launch_arena_optimizer_run(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                    triggered_by=triggered_by,
                )
                studio_state = registry_store.get_arena_optimizer_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
            except KeyError as exc:
                self._send_json({"status": "error", "code": "arena_not_found", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError:
                validation_report = registry_store.validate_arena_optimizer_setup(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                studio_state = registry_store.get_arena_optimizer_studio_state(
                    tenant_id=tenant_id,
                    owner_user_id=user_id,
                    arena_id=arena_id,
                )
                response_payload = _build_c5_optimizer_state_payload(arena_id=arena_id, studio_state=studio_state)
                response_payload["status"] = "error"
                response_payload["code"] = "optimizer_guardrail_blocked"
                response_payload["message"] = "Optimizer launch blocked by guardrails."
                response_payload["validation_report"] = validation_report
                self._send_json(response_payload, status=HTTPStatus.CONFLICT)
                return

            response_payload = _build_c5_optimizer_state_payload(arena_id=arena_id, studio_state=studio_state)
            response_payload["action"] = "launch_optimizer"
            response_payload["run"] = _build_c5_launch_entry(run_entry)
            self._send_json(response_payload, status=HTTPStatus.ACCEPTED)

        def _resolve_request_actor(self) -> tuple[str, str]:
            """Разрешает tenant/user контекст запроса из заголовков либо default окружения."""

            default_tenant_id, default_user_id = _resolve_default_actor()
            tenant_id = (self.headers.get("X-Demo-Tenant-Id") or default_tenant_id).strip() or default_tenant_id
            user_id = (self.headers.get("X-Demo-User-Id") or default_user_id).strip() or default_user_id
            return tenant_id, user_id

        def _handle_legacy_validate_compile(self) -> None:
            """Оставляет legacy C1 validate+compile как debug-route для обратной совместимости."""

            try:
                payload = self._read_json_body()
            except ValueError as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            dsl_file_raw = payload.get("dsl_file")
            if not isinstance(dsl_file_raw, str) or not dsl_file_raw.strip():
                self._send_json(
                    {"status": "error", "message": "Field `dsl_file` must be a non-empty string."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            dsl_file = (project_root / dsl_file_raw).resolve()
            if not str(dsl_file).startswith(str(project_root.resolve())):
                self._send_json(
                    {"status": "error", "message": "DSL file path must stay inside project workspace."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if not dsl_file.exists():
                self._send_json(
                    {"status": "error", "message": f"DSL file not found: {dsl_file_raw}"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                spec = load_dsl_spec(dsl_file)
            except (DslLoadError, DslValidationError) as exc:
                self._send_json(
                    {"status": "error", "message": str(exc), "dsl_file": dsl_file_raw},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            compile_result = DslToGraphIRCompiler().compile_file(dsl_file)
            compile_report = compile_result.report.model_dump()
            compile_summary = compile_result.report.summary()
            graph_ir_summary: dict[str, Any] = {"available": False}
            if compile_result.graph_ir is not None:
                graph_ir_summary = {
                    "available": True,
                    "entry_node": compile_result.graph_ir.entry_node,
                    "nodes_total": len(compile_result.graph_ir.nodes),
                    "edges_total": len(compile_result.graph_ir.edges),
                    "terminal_nodes": compile_result.graph_ir.terminal_nodes,
                }

            self._send_json(
                {
                    "status": "success",
                    "capability_id": "c1",
                    "dsl_file": dsl_file_raw,
                    "dsl_summary": spec.summary(),
                    "compile_summary": compile_summary,
                    "compile_report": compile_report,
                    "graph_ir_summary": graph_ir_summary,
                }
            )

        def log_message(self, format: str, *args: Any) -> None:
            """Переопределяет стандартный лог в stderr, чтобы сообщения были компактными."""

            sys.stderr.write("[FRONTEND] " + format % args + "\n")

        def _read_json_body(self) -> dict[str, Any]:
            """Читает JSON body входящего запроса и возвращает словарь."""

            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            if not raw_body:
                raise ValueError("Request body is empty.")
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON body: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object.")
            return payload

        def _send_json(self, payload: dict[str, Any], *, status: HTTPStatus = HTTPStatus.OK) -> None:
            """Отправляет JSON ответ с корректными заголовками content-type и длины."""

            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(int(status))
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    return FrontendRequestHandler


def main() -> None:
    """Точка входа для `python -m optimizer.frontend.dev_server`."""

    raise SystemExit(FrontendDevServerCli.run())


if __name__ == "__main__":
    main()
