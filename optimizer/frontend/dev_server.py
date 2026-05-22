"""Dev server frontend shell: СЃС‚Р°С‚РёС‡РµСЃРєРёР№ UI + РјРёРЅРёРјР°Р»СЊРЅС‹Р№ API РґР»СЏ capability-РїСЂРѕРІРµСЂРѕРє."""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.dsl.io import DslLoadError, DslValidationError, load_dsl_spec
from optimizer.frontend.contracts import build_capability_catalog_payload, build_stub_capability_payload


class FrontendDevServerCli:
    """CLI-РєРѕРјРїРѕРЅРµРЅС‚ Р·Р°РїСѓСЃРєР° frontend shell dev server."""

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """РЎРѕР·РґР°РµС‚ CLI-РїР°СЂСЃРµСЂ РґР»СЏ dev server."""

        parser = argparse.ArgumentParser(description="AutoAgent Optimizer frontend shell dev server")
        parser.add_argument("--host", default="127.0.0.1", help="РҐРѕСЃС‚ bind РґР»СЏ HTTP-СЃРµСЂРІРµСЂР°.")
        parser.add_argument("--port", type=int, default=4173, help="РџРѕСЂС‚ bind РґР»СЏ HTTP-СЃРµСЂРІРµСЂР°.")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        """Р—Р°РїСѓСЃРєР°РµС‚ HTTP-СЃРµСЂРІРµСЂ Рё РІРѕР·РІСЂР°С‰Р°РµС‚ РєРѕРґ Р·Р°РІРµСЂС€РµРЅРёСЏ РїСЂРѕС†РµСЃСЃР°."""

        parser = FrontendDevServerCli.build_parser()
        args = parser.parse_args(argv)

        project_root = Path(__file__).resolve().parents[2]
        handler_class = _build_handler(project_root=project_root)
        server = ThreadingHTTPServer((args.host, args.port), handler_class)

        print(f"[FRONTEND] dev server started at http://{args.host}:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0


def _build_handler(*, project_root: Path) -> type[SimpleHTTPRequestHandler]:
    """РЎРѕР·РґР°РµС‚ handler-РєР»Р°СЃСЃ СЃ Р·Р°РјС‹РєР°РЅРёРµРј РЅР° project_root, С‡С‚РѕР±С‹ API Рё static Р¶РёР»Рё РІ РѕРґРЅРѕРј СЃРµСЂРІРµСЂРµ."""

    class FrontendRequestHandler(SimpleHTTPRequestHandler):
        """HTTP handler РґР»СЏ frontend shell: static + C1..C6 API endpoints."""

        # Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РѕС‚РґР°С‘Рј СЃС‚Р°С‚РёРєСѓ РёР· РєРѕСЂРЅСЏ РїСЂРѕРµРєС‚Р°, С‡С‚РѕР±С‹ Р±С‹Р»Рё РґРѕСЃС‚СѓРїРЅС‹ `frontend/` Рё `design_system/`.
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(project_root), **kwargs)

        def do_GET(self) -> None:  # noqa: N802
            """РћР±СЂР°Р±Р°С‚С‹РІР°РµС‚ GET: health, capability-РєР°С‚Р°Р»РѕРі, stub-endpoints Рё СЃС‚Р°С‚РёРєСѓ."""

            if self.path == "/api/health":
                self._send_json({"status": "ok", "service": "frontend_dev_server"})
                return
            if self.path == "/api/capabilities":
                self._send_json(build_capability_catalog_payload())
                return
            if self.path in {"/api/c2/sample", "/api/c3/sample", "/api/c4/sample", "/api/c5/sample", "/api/c6/sample"}:
                capability_id = self.path.split("/")[2]
                self._send_json(build_stub_capability_payload(capability_id))
                return
            if self.path.startswith("/assets/"):
                # Русский комментарий: built index.html использует `/assets/*`, поэтому пробрасываем на `frontend/dist/assets/*`.
                dist_assets_path = project_root / "frontend" / "dist" / "assets"
                if dist_assets_path.exists():
                    self.path = f"/frontend/dist{self.path}"
            if self.path == "/" or self.path == "/index.html":
                # Русский комментарий: в режиме React/TS по умолчанию отдаем собранный dist entrypoint.
                dist_index_path = project_root / "frontend" / "dist" / "index.html"
                if dist_index_path.exists():
                    self.path = "/frontend/dist/index.html"
                else:
                    # Русский комментарий: fallback на исходный index для случаев, когда build еще не выполнен.
                    self.path = "/frontend/index.html"
            super().do_GET()

        def do_POST(self) -> None:  # noqa: N802
            """РћР±СЂР°Р±Р°С‚С‹РІР°РµС‚ POST: СЂРµР°Р»СЊРЅС‹Р№ C1 endpoint validate+compile."""

            if self.path != "/api/c1/validate-compile":
                self._send_json({"status": "error", "message": "Not found"}, status=HTTPStatus.NOT_FOUND)
                return

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
            # Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: Р·Р°С‰РёС‰Р°РµРј endpoint РѕС‚ РІС‹С…РѕРґР° Р·Р° РїСЂРµРґРµР»С‹ СЂР°Р±РѕС‡РµР№ РґРёСЂРµРєС‚РѕСЂРёРё РїСЂРѕРµРєС‚Р°.
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
            """РџРµСЂРµРѕРїСЂРµРґРµР»СЏРµС‚ СЃС‚Р°РЅРґР°СЂС‚РЅС‹Р№ Р»РѕРі РІ stderr, С‡С‚РѕР±С‹ СЃРѕРѕР±С‰РµРЅРёСЏ РѕСЃС‚Р°РІР°Р»РёСЃСЊ РєРѕРјРїР°РєС‚РЅС‹РјРё Рё С‡РёС‚Р°РµРјС‹РјРё."""

            sys.stderr.write("[FRONTEND] " + format % args + "\n")

        def _read_json_body(self) -> dict[str, Any]:
            """Р§РёС‚Р°РµС‚ JSON body РІС…РѕРґСЏС‰РµРіРѕ Р·Р°РїСЂРѕСЃР° Рё РІРѕР·РІСЂР°С‰Р°РµС‚ СЃР»РѕРІР°СЂСЊ."""

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
            """РћС‚РїСЂР°РІР»СЏРµС‚ JSON РѕС‚РІРµС‚ СЃ РєРѕСЂСЂРµРєС‚РЅС‹РјРё Р·Р°РіРѕР»РѕРІРєР°РјРё content-type Рё РґР»РёРЅС‹."""

            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(int(status))
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    return FrontendRequestHandler


def main() -> None:
    """РўРѕС‡РєР° РІС…РѕРґР° РґР»СЏ `python -m optimizer.frontend.dev_server`."""

    raise SystemExit(FrontendDevServerCli.run())


if __name__ == "__main__":
    main()

