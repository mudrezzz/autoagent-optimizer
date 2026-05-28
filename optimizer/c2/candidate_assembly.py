"""Внутренний процесс отбора кандидатов C2 и compile-readiness подготовки к тестам."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from optimizer.dsl.compile_report import CompileIssueSeverity, CompileStatus
from optimizer.dsl.compiler import DslToGraphIRCompiler


# Русский комментарий: каноничные DSL-стабы по pattern_ref для автоисправления распространенных несоответствий.
_PATTERN_DSL_FALLBACKS: dict[str, str] = {
    "style.direct_llm": "examples/dsl/style_direct_llm.yaml",
    "style.pattern_cleaner": "examples/dsl/style_pattern_cleaner.yaml",
    "style.hybrid_retriever": "examples/dsl/style_hybrid_retriever.yaml",
    "style.hitl_reviewer": "examples/dsl/style_hitl_reviewer.yaml",
}


def select_candidates_for_tests_and_prepare(
    *,
    candidate_set_draft: dict[str, Any],
    selected_candidate_ids: list[str] | tuple[str, ...],
    project_root: Path,
    max_compile_attempts: int = 3,
) -> dict[str, Any]:
    """Помечает выбранных кандидатов и внутренне готовит их к тестам через compile-readiness."""

    normalized_draft = deepcopy(candidate_set_draft)
    candidates_raw = normalized_draft.get("candidates")
    if not isinstance(candidates_raw, list):
        raise ValueError("candidate_set_draft.candidates must be an array.")

    normalized_selected_ids = _normalize_selected_candidate_ids(selected_candidate_ids)
    if not normalized_selected_ids:
        raise ValueError("Select at least one candidate for tests.")
    if max_compile_attempts < 1 or max_compile_attempts > 5:
        raise ValueError("max_compile_attempts must be in range [1, 5].")

    selected_id_set = set(normalized_selected_ids)
    available_ids = {str(candidate.get("candidate_id", "")) for candidate in candidates_raw if isinstance(candidate, dict)}
    missing_ids = sorted(selected_id_set - available_ids)
    if missing_ids:
        raise ValueError(f"Unknown candidate ids: {', '.join(missing_ids)}")

    compiler = DslToGraphIRCompiler()
    processed_at = _utc_now_iso()
    selected_total = 0
    prepared_total = 0
    failed_total = 0

    for candidate in candidates_raw:
        if not isinstance(candidate, dict):
            continue
        candidate_id = str(candidate.get("candidate_id", ""))
        is_selected = candidate_id in selected_id_set
        candidate["selected_for_tests"] = is_selected
        if not is_selected:
            continue

        selected_total += 1
        readiness = _prepare_candidate_with_retries(
            candidate=candidate,
            compiler=compiler,
            project_root=project_root,
            processed_at=processed_at,
            max_compile_attempts=max_compile_attempts,
        )
        candidate["compile_readiness"] = readiness
        if readiness["status"] == "ready":
            prepared_total += 1
        else:
            failed_total += 1

    gate_status = "ready" if selected_total > 0 and failed_total == 0 else "failed"
    normalized_draft["compile_gate"] = {
        "status": gate_status,
        "compiled_candidates": selected_total,
        "ready_candidates": prepared_total,
        "failed_candidates": failed_total,
        "selected_candidates": selected_total,
        "total_candidates": len(candidates_raw),
        "processed_at": processed_at,
        "max_compile_attempts": max_compile_attempts,
    }
    return normalized_draft


def _normalize_selected_candidate_ids(raw_selected_ids: list[str] | tuple[str, ...]) -> list[str]:
    """Нормализует список выбранных candidate_id в уникальный массив."""

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in raw_selected_ids:
        candidate_id = str(raw).strip()
        if not candidate_id or candidate_id in seen:
            continue
        seen.add(candidate_id)
        normalized.append(candidate_id)
    return normalized


def _prepare_candidate_with_retries(
    *,
    candidate: dict[str, Any],
    compiler: DslToGraphIRCompiler,
    project_root: Path,
    processed_at: str,
    max_compile_attempts: int,
) -> dict[str, Any]:
    """Запускает несколько внутренних итераций подготовки кандидата перед выдачей issue пользователю."""

    attempts_used = 0
    dsl_stub_ref = str(candidate.get("dsl_stub_ref", "")).strip()
    for _ in range(max_compile_attempts):
        attempts_used += 1
        readiness = _compile_single_candidate(
            candidate=candidate,
            compiler=compiler,
            project_root=project_root,
            processed_at=processed_at,
        )
        if readiness["status"] == "ready":
            readiness["attempts_used"] = attempts_used
            readiness["user_visible_issue"] = False
            return readiness

        auto_fix_applied = _try_auto_fix_candidate_dsl_ref(candidate=candidate, current_dsl_ref=dsl_stub_ref)
        if auto_fix_applied:
            dsl_stub_ref = str(candidate.get("dsl_stub_ref", "")).strip()
            continue
        break

    readiness["attempts_used"] = attempts_used
    readiness["user_visible_issue"] = True
    return readiness


def _try_auto_fix_candidate_dsl_ref(*, candidate: dict[str, Any], current_dsl_ref: str) -> bool:
    """Пробует автоисправить `dsl_stub_ref` по pattern_ref, если найден каноничный fallback."""

    pattern_ref = str(candidate.get("pattern_ref", "")).strip()
    fallback = _PATTERN_DSL_FALLBACKS.get(pattern_ref, "")
    if not fallback or fallback == current_dsl_ref:
        return False
    candidate["dsl_stub_ref"] = fallback
    return True


def _compile_single_candidate(
    *,
    candidate: dict[str, Any],
    compiler: DslToGraphIRCompiler,
    project_root: Path,
    processed_at: str,
) -> dict[str, Any]:
    """Компилирует DSL-кандидата и формирует readiness-отчет для внутреннего процесса подготовки."""

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
