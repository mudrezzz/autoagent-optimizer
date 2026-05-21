"""Parity-runner для структурной проверки DSL-vs-native исполнения."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from optimizer.champion.native_export import NativeLanggraphDaiExporter
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.evaluation.dataset_loader import GoldenDatasetLoader
from optimizer.evaluation.profile_schema import EvaluationProfileSpec
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer
from optimizer.renderer.langgraph_dai.run import _build_demo_bindings


@dataclass(frozen=True)
class ParityCaseResult:
    """Результат parity-сравнения для одного dataset-кейса у одного участника."""

    case_id: str
    passed: bool
    checks: dict[str, bool]
    mismatches: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        """Преобразует case-level parity результат в JSON-совместимую структуру."""

        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "checks": self.checks,
            "mismatches": self.mismatches,
        }


@dataclass(frozen=True)
class ParityParticipantResult:
    """Результат parity-сравнения по одному participant из evaluation profile."""

    participant_id: str
    source_kind: str
    source_path: str
    passed: bool
    cases_total: int
    cases_passed: int
    case_results: list[ParityCaseResult]

    def to_payload(self) -> dict[str, Any]:
        """Преобразует participant-level parity результат в JSON-совместимую структуру."""

        return {
            "participant_id": self.participant_id,
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "passed": self.passed,
            "cases_total": self.cases_total,
            "cases_passed": self.cases_passed,
            "case_results": [item.to_payload() for item in self.case_results],
        }


@dataclass(frozen=True)
class DslNativeParityReport:
    """Сводный отчет parity-проверки для всего evaluation profile."""

    version: str
    profile_id: str
    mode: str
    cases_checked_per_participant: int
    participants_total: int
    participants_passed: int
    participants_failed: int
    passed: bool
    participants: list[ParityParticipantResult]

    def to_payload(self) -> dict[str, Any]:
        """Преобразует parity-отчет в JSON-совместимую структуру для CLI/CI."""

        return {
            "version": self.version,
            "profile_id": self.profile_id,
            "mode": self.mode,
            "cases_checked_per_participant": self.cases_checked_per_participant,
            "participants_total": self.participants_total,
            "participants_passed": self.participants_passed,
            "participants_failed": self.participants_failed,
            "passed": self.passed,
            "participants": [item.to_payload() for item in self.participants],
        }


class DslNativeParityRunner:
    """Runner структурной parity-проверки `dsl_runtime` против `native_runtime`."""

    def run(
        self,
        *,
        profile: EvaluationProfileSpec,
        profile_file_dir: Path,
        cases_limit: int = 1,
        participant_ids: list[str] | None = None,
    ) -> DslNativeParityReport:
        """Запускает parity-сравнение по выбранным participant и dataset-кейсам profile."""

        selected_participants = _select_participants(profile=profile, participant_ids=participant_ids)
        parity_cases = _select_parity_cases(
            profile=profile,
            profile_file_dir=profile_file_dir,
            cases_limit=cases_limit,
        )
        participant_results: list[ParityParticipantResult] = []
        with _without_openrouter_api_key():
            for participant in selected_participants:
                graph_ir = _resolve_participant_graph_ir(participant=participant, base_dir=profile_file_dir)
                participant_result = self._run_participant(
                    participant_id=participant.participant_id,
                    source_kind="graph_ir" if str(participant.graph_ir_file).strip() else "dsl",
                    source_path=str(
                        _resolve_path(profile_file_dir, participant.graph_ir_file or participant.dsl_file)
                    ),
                    graph_ir=graph_ir,
                    cases=parity_cases,
                )
                participant_results.append(participant_result)

        participants_passed = sum(1 for item in participant_results if item.passed)
        participants_total = len(participant_results)
        participants_failed = participants_total - participants_passed
        effective_cases_limit = len(parity_cases)
        return DslNativeParityReport(
            version="dsl_native_parity_v0",
            profile_id=profile.profile_id,
            mode="mock_llm_for_stability",
            cases_checked_per_participant=effective_cases_limit,
            participants_total=participants_total,
            participants_passed=participants_passed,
            participants_failed=participants_failed,
            passed=(participants_failed == 0),
            participants=participant_results,
        )

    def _run_participant(
        self,
        *,
        participant_id: str,
        source_kind: str,
        source_path: str,
        graph_ir: GraphIRSpec,
        cases: list[dict[str, Any]],
    ) -> ParityParticipantResult:
        """Запускает parity-сравнение по всем выбранным кейсам для одного participant."""

        case_results: list[ParityCaseResult] = []
        for case in cases:
            case_id = str(case["case_id"])
            payload = dict(case["payload"])
            dsl_output = _run_dsl_runtime(graph_ir=graph_ir, payload=payload, task_id=f"parity-dsl-{case_id}")
            native_output = _run_native_runtime(
                graph_ir=graph_ir,
                payload=payload,
                export_name=f"parity_{_sanitize_id(participant_id)}_{_sanitize_id(case_id)}",
                task_id=f"parity-native-{case_id}",
            )
            case_results.append(compare_structural_state(case_id=case_id, dsl_state=dsl_output, native_state=native_output))

        cases_total = len(case_results)
        cases_passed = sum(1 for item in case_results if item.passed)
        return ParityParticipantResult(
            participant_id=participant_id,
            source_kind=source_kind,
            source_path=source_path,
            passed=(cases_passed == cases_total),
            cases_total=cases_total,
            cases_passed=cases_passed,
            case_results=case_results,
        )


def compare_structural_state(
    *,
    case_id: str,
    dsl_state: dict[str, Any],
    native_state: dict[str, Any],
) -> ParityCaseResult:
    """Сравнивает структурные сигналы исполнения одного кейса между DSL и native путями."""

    dsl_norm = _normalize_runtime_state(dsl_state)
    native_norm = _normalize_runtime_state(native_state)
    checks = {
        "executed_nodes_equal": dsl_norm["executed_nodes"] == native_norm["executed_nodes"],
        "skipped_nodes_equal": dsl_norm["skipped_nodes"] == native_norm["skipped_nodes"],
        "node_output_keys_equal": dsl_norm["node_output_keys"] == native_norm["node_output_keys"],
        "errors_equal": dsl_norm["errors"] == native_norm["errors"],
        "trace_topology_equal": dsl_norm["trace_topology"] == native_norm["trace_topology"],
    }
    mismatches: list[dict[str, Any]] = []
    for check_name, passed in checks.items():
        if passed:
            continue
        mismatches.append(
            {
                "check": check_name,
                "dsl": _truncate_for_report(dsl_norm[_check_to_key(check_name)]),
                "native": _truncate_for_report(native_norm[_check_to_key(check_name)]),
            }
        )
    return ParityCaseResult(
        case_id=case_id,
        passed=all(checks.values()),
        checks=checks,
        mismatches=mismatches,
    )


def _check_to_key(check_name: str) -> str:
    """Маппит имя проверки parity на имя нормализованного структурного поля."""

    mapping = {
        "executed_nodes_equal": "executed_nodes",
        "skipped_nodes_equal": "skipped_nodes",
        "node_output_keys_equal": "node_output_keys",
        "errors_equal": "errors",
        "trace_topology_equal": "trace_topology",
    }
    return mapping[check_name]


def _normalize_runtime_state(raw_state: dict[str, Any]) -> dict[str, Any]:
    """Нормализует runtime state в канонический набор структурных сигналов для сравнения."""

    executed_nodes = [str(item) for item in raw_state.get("executed_nodes", [])]
    skipped_nodes = [str(item) for item in raw_state.get("skipped_nodes", [])]
    errors = [str(item) for item in raw_state.get("errors", [])]
    trace = raw_state.get("trace", [])
    node_outputs = raw_state.get("node_outputs", {})

    normalized_trace: list[dict[str, Any]] = []
    if isinstance(trace, list):
        for item in trace:
            if not isinstance(item, dict):
                continue
            next_nodes_raw = item.get("next_nodes", [])
            next_nodes = sorted([str(node_id) for node_id in next_nodes_raw]) if isinstance(next_nodes_raw, list) else []
            normalized_trace.append(
                {
                    "node_id": str(item.get("node_id", "")),
                    "status": str(item.get("status", "")),
                    "next_nodes": next_nodes,
                }
            )

    output_keys_by_node: dict[str, list[str]] = {}
    if isinstance(node_outputs, dict):
        for node_id, node_output in node_outputs.items():
            normalized_node_id = str(node_id)
            if isinstance(node_output, dict):
                output_keys_by_node[normalized_node_id] = sorted([str(key) for key in node_output.keys()])
            else:
                output_keys_by_node[normalized_node_id] = ["<non_dict_output>"]

    return {
        "executed_nodes": executed_nodes,
        "skipped_nodes": skipped_nodes,
        "errors": errors,
        "node_output_keys": output_keys_by_node,
        "trace_topology": normalized_trace,
    }


def _truncate_for_report(value: Any, *, limit: int = 1200) -> Any:
    """Ограничивает длинные сериализуемые значения в parity-репорте для читаемости."""

    payload = json.dumps(value, ensure_ascii=False)
    if len(payload) <= limit:
        return value
    return {"truncated": True, "json_prefix": payload[:limit]}


def _select_participants(*, profile: EvaluationProfileSpec, participant_ids: list[str] | None) -> list[Any]:
    """Выбирает участников profile для parity-проверки по optional фильтру participant_ids."""

    participants = list(profile.participants)
    if not participant_ids:
        return participants
    allowed = {item.strip() for item in participant_ids if item.strip()}
    selected = [item for item in participants if item.participant_id in allowed]
    if not selected:
        raise ValueError("Ни один participant_id из фильтра не найден в profile.")
    return selected


def _select_parity_cases(
    *,
    profile: EvaluationProfileSpec,
    profile_file_dir: Path,
    cases_limit: int,
) -> list[dict[str, Any]]:
    """Выбирает ограниченный набор dataset-кейсов для parity-сравнения."""

    dataset_file = _resolve_path(profile_file_dir, profile.dataset_file)
    loader = GoldenDatasetLoader()
    dataset = loader.load_file(dataset_file)
    if dataset.issues:
        raise ValueError(f"Dataset содержит ошибки и не может быть использован в parity run: {dataset_file}")
    if not dataset.records:
        raise ValueError(f"Dataset пустой: {dataset_file}")

    requested_limit = cases_limit if cases_limit > 0 else profile.budget.cases_limit
    effective_limit = requested_limit if requested_limit > 0 else 1
    effective_limit = min(effective_limit, len(dataset.records))

    selector = profile.budget.selector
    if selector == "head":
        selected_records = dataset.records[:effective_limit]
    elif selector == "random_seeded":
        rnd = random.Random(profile.budget.random_seed)
        selected_records = rnd.sample(dataset.records, k=effective_limit)
    elif selector == "hash_stable":
        selected_records = _hash_stable_select(
            records=dataset.records,
            limit=effective_limit,
            random_seed=profile.budget.random_seed,
        )
    else:
        raise ValueError(f"Неподдержанный budget selector: {selector}")

    prepared_cases: list[dict[str, Any]] = []
    for record in selected_records:
        if not isinstance(record.input, dict):
            raise ValueError(f"Dataset case `{record.case_id}` имеет не-объект input, parity runner ожидает dict.")
        prepared_cases.append({"case_id": record.case_id, "payload": dict(record.input)})
    return prepared_cases


def _hash_stable_select(*, records: list[Any], limit: int, random_seed: int) -> list[Any]:
    """Стабильно выбирает `limit` кейсов через hash(case_id, seed) без случайного дрейфа."""

    sorted_records = sorted(
        records,
        key=lambda item: hashlib.sha256(f"{item.case_id}|{random_seed}".encode("utf-8")).hexdigest(),
    )
    return sorted_records[:limit]


def _resolve_participant_graph_ir(*, participant: Any, base_dir: Path) -> GraphIRSpec:
    """Резолвит Graph IR участника напрямую или через компиляцию DSL."""

    if str(participant.graph_ir_file).strip():
        return load_graph_ir_spec(_resolve_path(base_dir, participant.graph_ir_file))

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(_resolve_path(base_dir, participant.dsl_file))
    if compile_result.graph_ir is None:
        raise ValueError(
            f"Не удалось скомпилировать DSL участника `{participant.participant_id}`: {compile_result.report.summary()}"
        )
    return compile_result.graph_ir


def _resolve_path(base_dir: Path, path_value: str) -> Path:
    """Резолвит абсолютный путь или путь относительно директории profile."""

    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _run_dsl_runtime(*, graph_ir: GraphIRSpec, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
    """Запускает DSL runtime путь и возвращает структурное состояние исполнения."""

    runtime = GraphIRToLangGraphRenderer().render(graph_ir=graph_ir, bindings=_build_demo_bindings())
    state = runtime.invoke(payload=dict(payload), task_id=task_id)
    return {
        "executed_nodes": list(state.executed_nodes),
        "skipped_nodes": list(state.skipped_nodes),
        "errors": list(state.errors),
        "node_outputs": dict(state.node_outputs),
        "trace": list(state.trace),
    }


def _run_native_runtime(
    *,
    graph_ir: GraphIRSpec,
    payload: dict[str, Any],
    export_name: str,
    task_id: str,
) -> dict[str, Any]:
    """Запускает standalone native runtime путь через временный export package и возвращает его output."""

    tmp_root = Path(".") / "tmp" / "parity_runtime" / export_name
    export_result = NativeLanggraphDaiExporter().export(
        graph_ir=graph_ir,
        prompt_templates=_build_demo_bindings().prompt_templates,
        output_dir=tmp_root,
        force=True,
    )
    payload_file = export_result.output_dir / "payload.json"
    payload_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(export_result.run_file),
            "--payload-file",
            str(payload_file),
            "--task-id",
            task_id,
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=export_result.output_dir,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Native runtime parity run failed: "
            f"returncode={proc.returncode}, stderr={proc.stderr[-1200:]}"
        )
    try:
        output_payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Native runtime returned non-JSON output.") from exc
    return output_payload


def _sanitize_id(raw: str) -> str:
    """Нормализует идентификатор для безопасного имени временного каталога parity export."""

    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw.strip())
    normalized = normalized.strip("._-")
    return normalized or "item"


@contextlib.contextmanager
def _without_openrouter_api_key():
    """Временно отключает OPENROUTER_API_KEY для детерминированного mock-LLM parity сравнения."""

    previous = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = ""
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("OPENROUTER_API_KEY", None)
        else:
            os.environ["OPENROUTER_API_KEY"] = previous

