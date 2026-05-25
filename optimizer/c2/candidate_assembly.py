"""Сборка и compile-readiness gate для C2 candidate draft."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from optimizer.dsl.compile_report import CompileIssueSeverity, CompileStatus
from optimizer.dsl.compiler import DslToGraphIRCompiler


def run_compile_readiness_gate_for_candidate_set(
    *,
    candidate_set_draft: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    """Запускает compile-readiness gate для всех кандидатов и возвращает обновленный draft."""

    normalized_draft = deepcopy(candidate_set_draft)
    candidates_raw = normalized_draft.get("candidates")
    if not isinstance(candidates_raw, list):
        raise ValueError("candidate_set_draft.candidates must be an array.")

    compiler = DslToGraphIRCompiler()
    ready_candidates = 0
    failed_candidates = 0
    compiled_candidates = 0
    processed_at = _utc_now_iso()

    for candidate in candidates_raw:
        if not isinstance(candidate, dict):
            failed_candidates += 1
            continue
        readiness = _compile_single_candidate(
            candidate=candidate,
            compiler=compiler,
            project_root=project_root,
            processed_at=processed_at,
        )
        candidate["compile_readiness"] = readiness
        compiled_candidates += 1
        if readiness["status"] == "ready":
            ready_candidates += 1
        else:
            failed_candidates += 1

    gate_status = "ready" if compiled_candidates > 0 and failed_candidates == 0 else "failed"
    normalized_draft["compile_gate"] = {
        "status": gate_status,
        "compiled_candidates": compiled_candidates,
        "ready_candidates": ready_candidates,
        "failed_candidates": failed_candidates,
        "total_candidates": len(candidates_raw),
        "processed_at": processed_at,
    }
    return normalized_draft


def _compile_single_candidate(
    *,
    candidate: dict[str, Any],
    compiler: DslToGraphIRCompiler,
    project_root: Path,
    processed_at: str,
) -> dict[str, Any]:
    """Компилирует DSL-кандидата и формирует readiness-отчет для UI/API."""

    dsl_stub_ref = str(candidate.get("dsl_stub_ref", "")).strip()
    if not dsl_stub_ref:
        return _failed_readiness(
            dsl_file="",
            processed_at=processed_at,
            message="Field `dsl_stub_ref` is required for compile gate.",
            error_code="dsl_ref_missing",
        )

    dsl_file = (project_root / dsl_stub_ref).resolve()
    project_root_resolved = project_root.resolve()
    if not str(dsl_file).startswith(str(project_root_resolved)):
        return _failed_readiness(
            dsl_file=dsl_stub_ref,
            processed_at=processed_at,
            message="DSL path must stay inside project workspace.",
            error_code="dsl_path_outside_workspace",
        )

    compile_result = compiler.compile_file(dsl_file)
    summary = compile_result.report.summary()
    issues_payload = [
        {
            "severity": str(issue.severity.value),
            "message": issue.message,
            "context": dict(issue.context),
        }
        for issue in compile_result.report.issues
    ]
    graph_ir_summary = {
        "available": compile_result.graph_ir is not None,
        "entry_node": compile_result.graph_ir.entry_node if compile_result.graph_ir is not None else None,
        "nodes_total": len(compile_result.graph_ir.nodes) if compile_result.graph_ir is not None else 0,
        "edges_total": len(compile_result.graph_ir.edges) if compile_result.graph_ir is not None else 0,
        "terminal_nodes": list(compile_result.graph_ir.terminal_nodes) if compile_result.graph_ir is not None else [],
    }
    has_compile_errors = any(issue.severity == CompileIssueSeverity.ERROR for issue in compile_result.report.issues)
    is_ready = compile_result.report.status == CompileStatus.SUCCESS and not has_compile_errors and compile_result.graph_ir is not None

    return {
        "status": "ready" if is_ready else "failed",
        "dsl_file": dsl_stub_ref,
        "compile_summary": summary,
        "issues": issues_payload,
        "graph_ir_summary": graph_ir_summary,
        "compiled_at": processed_at,
    }


def _failed_readiness(*, dsl_file: str, processed_at: str, message: str, error_code: str) -> dict[str, Any]:
    """Возвращает унифицированный failed readiness-объект для кандидата."""

    return {
        "status": "failed",
        "dsl_file": dsl_file,
        "compile_summary": {
            "status": "failure",
            "source": dsl_file,
            "node_mappings": 0,
            "warnings": 0,
            "errors": 1,
        },
        "issues": [{"severity": "error", "message": message, "context": {"code": error_code}}],
        "graph_ir_summary": {"available": False, "entry_node": None, "nodes_total": 0, "edges_total": 0, "terminal_nodes": []},
        "compiled_at": processed_at,
    }


def _utc_now_iso() -> str:
    """Возвращает UTC timestamp для полей readiness-отчетов."""

    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
