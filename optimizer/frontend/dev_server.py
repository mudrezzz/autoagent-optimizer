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
from urllib.parse import urlparse

from optimizer.c2 import build_candidate_draft_from_brief
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


def _build_handler(*, project_root: Path, registry_store: WorkspaceRegistryStore) -> type[SimpleHTTPRequestHandler]:
    """Создает handler-класс с замыканием на project_root и registry_store."""

    class FrontendRequestHandler(SimpleHTTPRequestHandler):
        """HTTP handler для frontend shell: static + capability API + C1/C2 product API."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Инициализирует handler и настраивает root директорию раздачи статики."""

            super().__init__(*args, directory=str(project_root), **kwargs)

        def do_GET(self) -> None:  # noqa: N802
            """Обрабатывает GET-запросы API и static-файлов."""

            path = urlparse(self.path).path
            tenant_id, user_id = self._resolve_request_actor()
            if path == "/api/health":
                self._send_json({"status": "ok", "service": "frontend_dev_server"})
                return

            if path == "/api/capabilities":
                self._send_json(build_capability_catalog_payload())
                return

            if path in {"/api/c2/sample", "/api/c3/sample", "/api/c4/sample", "/api/c5/sample", "/api/c6/sample"}:
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

            candidate_set_draft: dict[str, Any] | None = None
            assistant_message: dict[str, Any] | None = None
            if generate_candidates:
                try:
                    candidate_set_draft = build_candidate_draft_from_brief(
                        arena_id=arena_id,
                        brief=message_raw,
                        max_candidates=max_candidates_raw,
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
