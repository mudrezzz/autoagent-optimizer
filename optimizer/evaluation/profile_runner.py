"""Runner profile-driven оценки задачи для `dsl_runtime` и `native_runtime` таргетов."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from optimizer.arena.runner import (
    ArenaParticipantResult,
    ArenaTournamentResult,
    ArchitectureArenaRunner,
    _apply_case_budget,
    _apply_scoring_policy,
    _build_node_stage_map,
    _rank_participants,
)
from optimizer.arena.tournament_schema import ArenaTournamentSpec
from optimizer.champion.native_export import NativeLanggraphDaiExporter
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.evaluation.dataset_loader import GoldenDatasetLoader
from optimizer.evaluation.dataset_schema import GoldenDatasetRecord
from optimizer.evaluation.oracle_runner import OracleRunner
from optimizer.evaluation.profile_schema import EvaluationExecutionTarget, EvaluationProfileSpec
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec, GraphNodeKind
from optimizer.metrics.diagnostic_signals import compute_diagnostic_signals
from optimizer.metrics.middle_metrics import compute_middle_metrics
from optimizer.renderer.langgraph_dai.run import _build_demo_bindings

NativeExecutionFn = Callable[[GoldenDatasetRecord], dict[str, Any]]


@dataclass(frozen=True)
class EvaluationProfileRunResult:
    """Итог profile-run с унифицированным envelope и метаданными профиля."""

    profile_id: str
    task_type: str
    version: str
    execution_target: EvaluationExecutionTarget
    arena_payload: dict[str, Any]
    evaluator_chain: list[dict[str, Any]]
    comparative_metrics: list[dict[str, Any]]
    diagnostic_signals: list[dict[str, Any]]
    budget: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        """Преобразует результат profile-run в JSON-совместимый отчет."""

        return {
            "profile_id": self.profile_id,
            "task_type": self.task_type,
            "version": self.version,
            "execution_target": self.execution_target,
            "evaluator_chain": self.evaluator_chain,
            "comparative_metrics": self.comparative_metrics,
            "diagnostic_signals": self.diagnostic_signals,
            "budget": self.budget,
            "result": self.arena_payload,
        }


class EvaluationProfileRunner:
    """Оркестратор запуска profile-driven оценки на поддерживаемом runtime-таргете."""

    def run(
        self,
        *,
        profile: EvaluationProfileSpec,
        profile_file_dir: Path,
        execution_target: EvaluationExecutionTarget,
        include_details: bool,
    ) -> EvaluationProfileRunResult:
        """Запускает evaluation profile на выбранном execution target."""

        if execution_target not in profile.supported_targets:
            raise ValueError(
                f"Target `{execution_target}` не поддержан профилем `{profile.profile_id}`. "
                f"Доступно: {', '.join(profile.supported_targets)}"
            )

        evaluator_types = [item.evaluator_type for item in profile.evaluators]
        if evaluator_types != ["golden_oracle"]:
            raise ValueError(
                "Evaluation Profile v0 поддерживает только evaluator chain `['golden_oracle']`. "
                f"Получено: {evaluator_types}"
            )

        if execution_target == "dsl_runtime":
            arena_payload = self._run_dsl_target(
                profile=profile,
                profile_file_dir=profile_file_dir,
                include_details=include_details,
            )
        else:
            arena_payload = self._run_native_target(
                profile=profile,
                profile_file_dir=profile_file_dir,
                include_details=include_details,
            )

        return EvaluationProfileRunResult(
            profile_id=profile.profile_id,
            task_type=profile.task_type,
            version=profile.version,
            execution_target=execution_target,
            evaluator_chain=[item.model_dump() for item in profile.evaluators],
            comparative_metrics=[item.model_dump() for item in profile.comparative_metrics],
            diagnostic_signals=[item.model_dump() for item in profile.diagnostic_signals],
            budget=profile.budget.model_dump(),
            arena_payload=arena_payload,
        )

    def _run_dsl_target(
        self,
        *,
        profile: EvaluationProfileSpec,
        profile_file_dir: Path,
        include_details: bool,
    ) -> dict[str, Any]:
        """Запускает профиль через существующий DSL runtime путь Arena."""

        arena_spec = _build_arena_spec_from_profile(profile=profile)
        runner = ArchitectureArenaRunner()
        result = runner.run(spec=arena_spec, arena_file_dir=profile_file_dir, include_details=include_details)
        return result.to_payload()

    def _run_native_target(
        self,
        *,
        profile: EvaluationProfileSpec,
        profile_file_dir: Path,
        include_details: bool,
    ) -> dict[str, Any]:
        """Запускает профиль на standalone native runtime, экспортируя кандидатов во временный каталог."""

        dataset_path = _resolve_path(profile_file_dir, profile.dataset_file)
        loader = GoldenDatasetLoader()
        dataset_result = loader.load_file(dataset_path)
        if not dataset_result.is_success:
            issues_text = "; ".join(f"line={item.line_number}: {item.message}" for item in dataset_result.issues)
            raise ValueError(f"Невалидный dataset для native profile-run: {issues_text}")

        arena_spec = _build_arena_spec_from_profile(profile=profile)
        selected_records = _apply_case_budget(dataset_result.records, arena_spec)
        if not selected_records:
            raise ValueError("После применения profile budget не осталось кейсов для native-runtime прогона.")

        oracle_runner = OracleRunner()
        participant_results: list[ArenaParticipantResult] = []
        prompt_templates = _build_demo_bindings().prompt_templates
        with tempfile.TemporaryDirectory(prefix="profile_native_runtime_") as tmp_dir_raw:
            tmp_dir = Path(tmp_dir_raw)
            for participant in profile.participants:
                graph_ir = _resolve_participant_graph_ir(participant=participant, base_dir=profile_file_dir)
                participant_runtime_dir = tmp_dir / participant.participant_id
                NativeLanggraphDaiExporter().export(
                    graph_ir=graph_ir,
                    prompt_templates=prompt_templates,
                    output_dir=participant_runtime_dir,
                    force=True,
                )
                run_file = participant_runtime_dir / "app" / "run.py"
                if not run_file.exists():
                    raise ValueError(
                        f"Native runtime entrypoint не найден для `{participant.participant_id}`: {run_file}"
                    )
                llm_node_ids = {node.id for node in graph_ir.nodes if node.kind == GraphNodeKind.LLM}
                execute_fn = _build_native_executor(
                    run_file=run_file,
                    runtime_dir=participant_runtime_dir,
                    task_prefix=profile.task_prefix,
                    participant_id=participant.participant_id,
                    llm_node_ids=llm_node_ids,
                )
                run_result = oracle_runner.run(selected_records, execute_fn)
                full_report = run_result.full_payload()
                middle_metrics = compute_middle_metrics(full_report).to_payload()
                node_stage_map = _build_node_stage_map(graph_ir=graph_ir)
                diagnostic_signals = compute_diagnostic_signals(full_report, node_stage_map=node_stage_map)
                source_kind, source_path = _participant_source(participant=participant, base_dir=profile_file_dir)
                participant_results.append(
                    ArenaParticipantResult(
                        participant_id=participant.participant_id,
                        source_kind=source_kind,
                        source_path=source_path,
                        cases_budget=len(selected_records),
                        cases_total=run_result.cases_total,
                        passed=run_result.passed,
                        failed=run_result.failed,
                        pass_rate=run_result.pass_rate,
                        middle_metrics=middle_metrics,
                        diagnostic_signals=diagnostic_signals,
                        oracle_report=(full_report if include_details else None),
                    )
                )

        _apply_scoring_policy(participant_results, arena_spec)
        sorted_results = _rank_participants(participant_results, arena_spec.ranking.metrics)
        ranking = [item.participant_id for item in sorted_results]
        winner_id = ranking[0]
        ranking_policy = [{"name": metric.name, "direction": metric.direction} for metric in arena_spec.ranking.metrics]
        native_result = ArenaTournamentResult(
            dataset_file=str(dataset_path),
            execution_mode="native_runtime",
            evaluator_mode=arena_spec.evaluator.mode,
            budget_policy=arena_spec.budget.policy,
            budget_unit=arena_spec.budget.unit,
            budget_selector=arena_spec.budget.selector,
            budget_limit=arena_spec.budget.limit,
            budget_seed=arena_spec.budget.random_seed,
            scoring_enabled=arena_spec.scoring.enabled,
            scoring_normalization=arena_spec.scoring.normalization,
            scoring_policy=[
                {"name": metric.name, "direction": metric.direction, "weight": metric.weight}
                for metric in arena_spec.scoring.metrics
            ],
            cases_budget=len(selected_records),
            dataset_records_total=len(dataset_result.records),
            evaluated_records_total=len(selected_records),
            ranking_policy=ranking_policy,
            winner_id=winner_id,
            ranking=ranking,
            participants=sorted_results,
        )
        return native_result.to_payload()


def _build_arena_spec_from_profile(profile: EvaluationProfileSpec) -> ArenaTournamentSpec:
    """Конвертирует evaluation profile в внутренний ArenaTournamentSpec."""

    scoring_metrics = [
        {
            "name": metric.metric_id,
            "direction": metric.direction,
            "weight": metric.weight,
        }
        for metric in profile.comparative_metrics
    ]
    ranking_metrics: list[dict[str, str]] = [{"name": "composite_score", "direction": "desc"}]
    seen_metric_names = {"composite_score"}
    for metric in profile.comparative_metrics:
        if metric.metric_id in seen_metric_names:
            continue
        ranking_metrics.append({"name": metric.metric_id, "direction": metric.direction})
        seen_metric_names.add(metric.metric_id)
    if "participant_id" not in seen_metric_names:
        ranking_metrics.append({"name": "participant_id", "direction": "asc"})

    return ArenaTournamentSpec.model_validate(
        {
            "version": "arena_v0",
            "dataset_file": profile.dataset_file,
            "execution_mode": profile.dsl_execution_mode,
            "task_prefix": profile.task_prefix,
            "budget": {
                "policy": "equal_cases",
                "unit": "cases",
                "selector": profile.budget.selector,
                "limit": profile.budget.cases_limit,
                "random_seed": profile.budget.random_seed,
            },
            "ranking": {"metrics": ranking_metrics},
            "scoring": {
                "enabled": True,
                "normalization": "minmax",
                "metrics": scoring_metrics,
            },
            "evaluator": {"mode": "rule_based_v0"},
            "participants": [participant.model_dump() for participant in profile.participants],
        }
    )


def _resolve_participant_graph_ir(*, participant: Any, base_dir: Path) -> GraphIRSpec:
    """Разрешает Graph IR участника из JSON или через компиляцию DSL."""

    if str(participant.graph_ir_file).strip():
        return load_graph_ir_spec(_resolve_path(base_dir, participant.graph_ir_file))

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(_resolve_path(base_dir, participant.dsl_file))
    if compile_result.graph_ir is None:
        raise ValueError(
            f"Не удалось скомпилировать DSL участника `{participant.participant_id}`: {compile_result.report.summary()}"
        )
    return compile_result.graph_ir


def _participant_source(*, participant: Any, base_dir: Path) -> tuple[str, str]:
    """Возвращает тип и абсолютный путь source-спеки участника."""

    if str(participant.graph_ir_file).strip():
        return "graph_ir", str(_resolve_path(base_dir, participant.graph_ir_file))
    return "dsl", str(_resolve_path(base_dir, participant.dsl_file))


def _resolve_path(base_dir: Path, path_value: str) -> Path:
    """Резолвит путь как абсолютный или относительно директории profile файла."""

    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _build_native_executor(
    *,
    run_file: Path,
    runtime_dir: Path,
    task_prefix: str,
    participant_id: str,
    llm_node_ids: set[str],
) -> NativeExecutionFn:
    """Строит executor кейсов через standalone native runtime entrypoint."""

    def _execute(record: GoldenDatasetRecord) -> dict[str, Any]:
        """Выполняет один кейс через subprocess-вызов native runtime."""

        start_ts = time.perf_counter()
        payload_file = runtime_dir / f"tmp_case_{record.case_id}.json"
        payload_file.write_text(json.dumps(record.input, ensure_ascii=False), encoding="utf-8")
        task_id = f"{task_prefix}-{participant_id}-{record.case_id}"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(run_file),
                    "--payload-file",
                    str(payload_file),
                    "--task-id",
                    task_id,
                ],
                capture_output=True,
                text=True,
                cwd=runtime_dir,
                check=False,
            )
        finally:
            payload_file.unlink(missing_ok=True)

        duration_ms = int((time.perf_counter() - start_ts) * 1000)
        if proc.returncode != 0:
            stderr_tail = (proc.stderr or "")[-1000:]
            raise ValueError(
                f"Native runtime case failed for participant `{participant_id}`, case `{record.case_id}`: {stderr_tail}"
            )

        try:
            raw_output = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Native runtime вернул не-JSON output для participant `{participant_id}`, case `{record.case_id}`."
            ) from exc

        if not isinstance(raw_output, dict):
            raise ValueError(
                f"Native runtime output должен быть JSON-объектом для participant `{participant_id}`, case `{record.case_id}`."
            )

        payload = raw_output.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        executed_nodes = raw_output.get("executed_nodes")
        if not isinstance(executed_nodes, list):
            executed_nodes = []
        node_outputs = raw_output.get("node_outputs")
        if not isinstance(node_outputs, dict):
            node_outputs = {}
        llm_calls = sum(1 for node_id in executed_nodes if isinstance(node_id, str) and node_id in llm_node_ids)

        text_value = payload.get("text")
        text = str(text_value) if text_value is not None else ""
        return {
            "text": text,
            "payload": payload,
            "node_outputs": node_outputs,
            "executed_nodes": executed_nodes,
            "trace_summary": {
                "completed": len(executed_nodes),
                "duration_ms": duration_ms,
                "task_id": raw_output.get("task_id", task_id),
            },
            "llm_calls": llm_calls,
            "errors": raw_output.get("errors", []),
        }

    return _execute
