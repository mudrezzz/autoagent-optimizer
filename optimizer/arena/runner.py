"""Исполняемый runner турнира Architecture Arena v0."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from optimizer.arena.tournament_schema import (
    ArenaParticipantSpec,
    ArenaRankingMetricSpec,
    ArenaScoringMetricSpec,
    ArenaTournamentSpec,
)
from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.evaluation.dataset_loader import GoldenDatasetLoader
from optimizer.evaluation.dataset_schema import GoldenDatasetRecord
from optimizer.evaluation.oracle_runner import OracleRunner
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec, GraphNodeKind
from optimizer.metrics.diagnostic_signals import compute_diagnostic_signals
from optimizer.metrics.middle_metrics import compute_middle_metrics
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer
from optimizer.renderer.langgraph_dai.run import _build_demo_bindings

ArenaExecutionFn = Callable[[GoldenDatasetRecord], dict[str, Any]]


@dataclass
class ArenaParticipantResult:
    """Итоговый результат одного участника в турнирном прогоне."""

    participant_id: str
    source_kind: str
    source_path: str
    cases_budget: int
    cases_total: int
    passed: int
    failed: int
    pass_rate: float
    middle_metrics: dict[str, float | int]
    composite_score: float | None = None
    score_breakdown: dict[str, Any] | None = None
    diagnostic_signals: dict[str, Any] | None = None
    oracle_report: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        """Преобразует результат участника в JSON-совместимый словарь."""

        payload: dict[str, Any] = {
            "participant_id": self.participant_id,
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "cases_budget": self.cases_budget,
            "cases_total": self.cases_total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "middle_metrics": self.middle_metrics,
        }
        if self.composite_score is not None:
            payload["composite_score"] = self.composite_score
        if self.score_breakdown is not None:
            payload["score_breakdown"] = self.score_breakdown
        if self.diagnostic_signals is not None:
            payload["diagnostic_signals"] = self.diagnostic_signals
        if self.oracle_report is not None:
            payload["oracle_report"] = self.oracle_report
        return payload


@dataclass
class ArenaTournamentResult:
    """Итог турнира между несколькими архитектурными кандидатами."""

    dataset_file: str
    execution_mode: str
    evaluator_mode: str
    budget_policy: str
    budget_unit: str
    budget_selector: str
    budget_limit: int
    budget_seed: int
    scoring_enabled: bool
    scoring_normalization: str
    scoring_policy: list[dict[str, Any]]
    cases_budget: int
    dataset_records_total: int
    evaluated_records_total: int
    ranking_policy: list[dict[str, str]]
    winner_id: str
    ranking: list[str]
    participants: list[ArenaParticipantResult] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        """Преобразует итог турнира в JSON-совместимую структуру."""

        participant_payloads = [participant.to_payload() for participant in self.participants]
        comparison_participants = [_build_comparison_participant_payload(item) for item in self.participants]
        diagnostics_participants = [_build_diagnostics_participant_payload(item) for item in self.participants]
        return {
            "dataset_file": self.dataset_file,
            "execution_mode": self.execution_mode,
            "evaluator_mode": self.evaluator_mode,
            "budget_policy": self.budget_policy,
            "budget_unit": self.budget_unit,
            "budget_selector": self.budget_selector,
            "budget_limit": self.budget_limit,
            "budget_seed": self.budget_seed,
            "scoring_enabled": self.scoring_enabled,
            "scoring_normalization": self.scoring_normalization,
            "scoring_policy": self.scoring_policy,
            "cases_budget": self.cases_budget,
            "dataset_records_total": self.dataset_records_total,
            "evaluated_records_total": self.evaluated_records_total,
            "ranking_policy": self.ranking_policy,
            "winner_id": self.winner_id,
            "ranking": self.ranking,
            "participants": participant_payloads,
            "comparison": {
                "winner_id": self.winner_id,
                "ranking": self.ranking,
                "ranking_policy": self.ranking_policy,
                "participants": comparison_participants,
            },
            "diagnostics": {
                "participants": diagnostics_participants,
            },
        }


class ArchitectureArenaRunner:
    """Runner турнирного сравнения архитектур в равном бюджете по кейсам."""

    def run(
        self,
        spec: ArenaTournamentSpec,
        arena_file_dir: Path,
        include_details: bool = False,
    ) -> ArenaTournamentResult:
        """Запускает турнир по конфигурации и возвращает итоговый отчет."""

        if spec.evaluator.mode != "rule_based_v0":
            raise ValueError(f"Неподдерживаемый evaluator mode: {spec.evaluator.mode}")

        dataset_path = _resolve_path(arena_file_dir, spec.dataset_file)
        loader = GoldenDatasetLoader()
        dataset_result = loader.load_file(dataset_path)
        if not dataset_result.is_success:
            issues_text = "; ".join(f"line={item.line_number}: {item.message}" for item in dataset_result.issues)
            raise ValueError(f"Невалидный dataset для Arena: {issues_text}")

        selected_records = _apply_case_budget(dataset_result.records, spec)
        if not selected_records:
            raise ValueError("После применения budget policy не осталось кейсов для турнира.")

        participant_results: list[ArenaParticipantResult] = []
        oracle_runner = OracleRunner()
        for participant in spec.participants:
            participant_graph_ir = _resolve_participant_graph_ir_for_diagnostics(
                participant=participant,
                arena_file_dir=arena_file_dir,
                execution_mode=spec.execution_mode,
            )
            execute_fn = _build_participant_executor(
                participant=participant,
                execution_mode=spec.execution_mode,
                arena_file_dir=arena_file_dir,
                task_prefix=spec.task_prefix,
                graph_ir=participant_graph_ir,
            )
            run_result = oracle_runner.run(selected_records, execute_fn)
            full_report = run_result.full_payload()
            middle_metrics = compute_middle_metrics(full_report).to_payload()
            node_stage_map = _build_node_stage_map(participant_graph_ir) if participant_graph_ir is not None else {}
            diagnostic_signals = compute_diagnostic_signals(full_report, node_stage_map=node_stage_map)
            source_kind, source_path = _participant_source(participant, arena_file_dir)
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

        _apply_scoring_policy(participant_results, spec)
        sorted_results = _rank_participants(participant_results, spec.ranking.metrics)
        ranking = [item.participant_id for item in sorted_results]
        winner_id = ranking[0]

        ranking_policy = [{"name": metric.name, "direction": metric.direction} for metric in spec.ranking.metrics]
        return ArenaTournamentResult(
            dataset_file=str(dataset_path),
            execution_mode=spec.execution_mode,
            evaluator_mode=spec.evaluator.mode,
            budget_policy=spec.budget.policy,
            budget_unit=spec.budget.unit,
            budget_selector=spec.budget.selector,
            budget_limit=spec.budget.limit,
            budget_seed=spec.budget.random_seed,
            scoring_enabled=spec.scoring.enabled,
            scoring_normalization=spec.scoring.normalization,
            scoring_policy=[
                {"name": metric.name, "direction": metric.direction, "weight": metric.weight}
                for metric in spec.scoring.metrics
            ],
            cases_budget=len(selected_records),
            dataset_records_total=len(dataset_result.records),
            evaluated_records_total=len(selected_records),
            ranking_policy=ranking_policy,
            winner_id=winner_id,
            ranking=ranking,
            participants=sorted_results,
        )


def _rank_participants(
    participants: list[ArenaParticipantResult],
    metrics: list[ArenaRankingMetricSpec],
) -> list[ArenaParticipantResult]:
    """Сортирует участников по config-driven ranking policy."""

    sorted_results = list(participants)
    for metric in reversed(metrics):
        reverse = metric.direction == "desc"
        sorted_results.sort(key=lambda item, metric_name=metric.name: _metric_value(item, metric_name), reverse=reverse)
    return sorted_results


def _metric_value(participant: ArenaParticipantResult, metric_name: str) -> Any:
    """Возвращает значение конкретной метрики ранжирования участника."""

    if metric_name == "pass_rate":
        return participant.pass_rate
    if metric_name == "passed":
        return participant.passed
    if metric_name == "failed":
        return participant.failed
    if metric_name == "participant_id":
        return participant.participant_id
    if metric_name == "composite_score":
        if participant.composite_score is None:
            raise ValueError("Метрика `composite_score` недоступна: scoring policy отключена.")
        return participant.composite_score
    if metric_name in participant.middle_metrics:
        return participant.middle_metrics[metric_name]
    raise ValueError(f"Неподдерживаемая метрика ранжирования: {metric_name}")


def _apply_scoring_policy(participants: list[ArenaParticipantResult], spec: ArenaTournamentSpec) -> None:
    """Рассчитывает composite score и вклад метрик для каждого участника по scoring policy."""

    if not spec.scoring.enabled:
        return
    if spec.scoring.normalization != "minmax":
        raise ValueError(f"Неподдерживаемая стратегия нормализации scoring: {spec.scoring.normalization}")

    values_by_participant = {item.participant_id: _participant_numeric_metrics(item) for item in participants}
    metric_bounds = _compute_metric_bounds(values_by_participant, spec.scoring.metrics)
    weight_total = sum(metric.weight for metric in spec.scoring.metrics)
    if weight_total <= 0:
        raise ValueError("Сумма весов scoring policy должна быть положительной.")

    for participant in participants:
        numeric_metrics = values_by_participant[participant.participant_id]
        breakdown: dict[str, dict[str, float | str]] = {}
        weighted_sum = 0.0
        for metric in spec.scoring.metrics:
            raw_value = float(numeric_metrics.get(metric.name, 0.0))
            min_value, max_value = metric_bounds[metric.name]
            normalized_value = _normalize_minmax(raw_value, min_value, max_value, metric.direction)
            weighted_value = normalized_value * metric.weight
            weighted_sum += weighted_value
            breakdown[metric.name] = {
                "direction": metric.direction,
                "raw_value": _round_float(raw_value),
                "normalized_value": _round_float(normalized_value),
                "weight": _round_float(metric.weight),
                "weighted_value": _round_float(weighted_value),
            }
        participant.composite_score = _round_float(weighted_sum / weight_total)
        participant.score_breakdown = breakdown


def _participant_numeric_metrics(participant: ArenaParticipantResult) -> dict[str, float]:
    """Возвращает числовой вектор метрик участника для scoring и ranking."""

    metrics: dict[str, float] = {
        "pass_rate": float(participant.pass_rate),
        "passed": float(participant.passed),
        "failed": float(participant.failed),
    }
    for key, value in participant.middle_metrics.items():
        if isinstance(value, (int, float)):
            metrics[key] = float(value)
    return metrics


def _compute_metric_bounds(
    values_by_participant: dict[str, dict[str, float]],
    metrics: list[ArenaScoringMetricSpec],
) -> dict[str, tuple[float, float]]:
    """Считает min/max границы каждой scoring-метрики по всем участникам турнира."""

    bounds: dict[str, tuple[float, float]] = {}
    for metric in metrics:
        values = [participant_values.get(metric.name, 0.0) for participant_values in values_by_participant.values()]
        if not values:
            bounds[metric.name] = (0.0, 0.0)
            continue
        bounds[metric.name] = (min(values), max(values))
    return bounds


def _normalize_minmax(raw_value: float, min_value: float, max_value: float, direction: str) -> float:
    """Нормализует значение метрики в диапазон [0..1] с учетом направления оптимизации."""

    if max_value <= min_value:
        return 1.0

    normalized = (raw_value - min_value) / (max_value - min_value)
    if direction == "asc":
        return 1.0 - normalized
    return normalized


def _round_float(value: float) -> float:
    """Округляет вещественное значение для стабильного и читаемого JSON-вывода."""

    return round(value, 6)


def _apply_case_budget(records: list[GoldenDatasetRecord], spec: ArenaTournamentSpec) -> list[GoldenDatasetRecord]:
    """Применяет config-driven budget selector и limit к набору кейсов."""

    if spec.budget.unit != "cases":
        raise ValueError(f"Неподдерживаемая единица бюджета: {spec.budget.unit}")
    if spec.budget.policy != "equal_cases":
        raise ValueError(f"Неподдерживаемая budget policy: {spec.budget.policy}")

    limit = spec.budget.limit
    if limit <= 0 or limit >= len(records):
        return list(records)

    if spec.budget.selector == "head":
        return list(records[:limit])

    if spec.budget.selector == "random_seeded":
        rng = random.Random(spec.budget.random_seed)
        sampled_indexes = rng.sample(range(len(records)), k=limit)
        sampled_indexes.sort()
        return [records[index] for index in sampled_indexes]

    if spec.budget.selector == "hash_stable":
        keyed_records = sorted(
            records,
            key=lambda record: _stable_hash(f"{spec.budget.random_seed}:{record.case_id}"),
        )
        return list(keyed_records[:limit])

    raise ValueError(f"Неподдерживаемый budget selector: {spec.budget.selector}")


def _stable_hash(value: str) -> str:
    """Возвращает стабильный sha256-хеш для детерминированной сортировки кейсов."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _build_participant_executor(
    participant: ArenaParticipantSpec,
    execution_mode: str,
    arena_file_dir: Path,
    task_prefix: str,
    graph_ir: GraphIRSpec | None = None,
) -> ArenaExecutionFn:
    """Строит функцию исполнения одного кейса для конкретного участника."""

    if execution_mode == "expected_stub":
        return _build_stub_executor(participant)

    if graph_ir is None:
        graph_ir = _resolve_participant_graph_ir(participant, arena_file_dir)
    llm_node_ids = {node.id for node in graph_ir.nodes if node.kind == GraphNodeKind.LLM}
    renderer = GraphIRToLangGraphRenderer()
    runtime = renderer.render(graph_ir=graph_ir, bindings=_build_demo_bindings())

    def _execute_runtime(record: GoldenDatasetRecord) -> dict[str, Any]:
        """Выполняет кейс через runtime workflow участника."""

        task_id = f"{task_prefix}-{participant.participant_id}-{record.case_id}"
        state = runtime.invoke(payload=record.input, task_id=task_id)
        payload = state.payload if isinstance(state.payload, dict) else {"raw_payload": str(state.payload)}
        text = payload.get("text", "")
        llm_calls = sum(1 for node_id in state.executed_nodes if node_id in llm_node_ids)
        return {
            "text": str(text),
            "payload": payload,
            "node_outputs": state.node_outputs,
            "executed_nodes": state.executed_nodes,
            "trace_summary": state.trace_summary,
            "llm_calls": llm_calls,
        }

    return _execute_runtime


def _build_stub_executor(participant: ArenaParticipantSpec) -> ArenaExecutionFn:
    """Создает deterministic executor участника для smoke/CI режима."""

    def _execute(record: GoldenDatasetRecord) -> dict[str, Any]:
        """Возвращает deterministic payload ответа согласно stub-профилю."""

        behavior = participant.stub_behavior
        if behavior == "fail_all":
            return {"text": "stub generic response"}
        if behavior == "fail_sensitive":
            if "sensitive" in record.tags:
                forbidden = record.expected.get("forbidden")
                if isinstance(forbidden, list) and forbidden:
                    return {"text": f"stub includes forbidden: {forbidden[0]}"}
                return {"text": "stub sensitive fallback"}
            return {"text": _build_perfect_text(record)}
        return {"text": _build_perfect_text(record)}

    return _execute


def _build_perfect_text(record: GoldenDatasetRecord) -> str:
    """Собирает deterministic текст, удовлетворяющий `must_include` условиям кейса."""

    must_include = record.expected.get("must_include")
    parts = [item for item in must_include if isinstance(item, str)] if isinstance(must_include, list) else []
    if not parts:
        parts = [f"stub-answer-{record.case_id}"]
    return ". ".join(parts)


def _resolve_participant_graph_ir(participant: ArenaParticipantSpec, arena_file_dir: Path):
    """Разрешает Graph IR участника напрямую или через компиляцию DSL."""

    if participant.graph_ir_file.strip():
        return load_graph_ir_spec(_resolve_path(arena_file_dir, participant.graph_ir_file))

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(_resolve_path(arena_file_dir, participant.dsl_file))
    if compile_result.graph_ir is None:
        raise ValueError(
            f"Не удалось скомпилировать DSL участника `{participant.participant_id}`: {compile_result.report.summary()}"
        )
    return compile_result.graph_ir


def _resolve_participant_graph_ir_for_diagnostics(
    *,
    participant: ArenaParticipantSpec,
    arena_file_dir: Path,
    execution_mode: str,
) -> GraphIRSpec | None:
    """Best-effort резолвит Graph IR для stage diagnostics без риска уронить expected_stub unit-тесты."""

    if execution_mode == "runtime":
        return _resolve_participant_graph_ir(participant, arena_file_dir)

    try:
        return _resolve_participant_graph_ir(participant, arena_file_dir)
    except (ValueError, FileNotFoundError, json.JSONDecodeError):
        # В expected_stub режиме source-файлы могут быть фиктивными (unit-тесты);
        # fallback на empty stage map допустим, чтобы не ломать deterministic проверки.
        return None


def _participant_source(participant: ArenaParticipantSpec, arena_file_dir: Path) -> tuple[str, str]:
    """Возвращает тип и абсолютный путь источника спецификации участника."""

    if participant.graph_ir_file.strip():
        return "graph_ir", str(_resolve_path(arena_file_dir, participant.graph_ir_file))
    return "dsl", str(_resolve_path(arena_file_dir, participant.dsl_file))


def _resolve_path(base_dir: Path, path_value: str) -> Path:
    """Резолвит путь относительно директории arena-конфига или как абсолютный путь."""

    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _build_node_stage_map(graph_ir: GraphIRSpec) -> dict[str, str]:
    """Строит map `node_id -> stage` для вычисления диагностических сигналов."""

    stage_map: dict[str, str] = {}
    for node in graph_ir.nodes:
        stage_map[node.id] = _stage_for_node_kind(node.kind)
    return stage_map


def _stage_for_node_kind(node_kind: GraphNodeKind) -> str:
    """Маппит тип узла Graph IR в унифицированную stage taxonomy."""

    if node_kind == GraphNodeKind.LLM:
        return "synthesize"
    if node_kind == GraphNodeKind.DETERMINISTIC:
        return "transform"
    if node_kind == GraphNodeKind.TOOL:
        return "tool_call"
    if node_kind == GraphNodeKind.VALIDATOR:
        return "validate"
    if node_kind == GraphNodeKind.HITL_GATE:
        return "hitl"
    return "unknown"


def _build_comparison_participant_payload(participant: ArenaParticipantResult) -> dict[str, Any]:
    """Возвращает comparison-часть участника (только сравнительные метрики)."""

    payload: dict[str, Any] = {
        "participant_id": participant.participant_id,
        "passed": participant.passed,
        "failed": participant.failed,
        "pass_rate": participant.pass_rate,
        "middle_metrics": participant.middle_metrics,
    }
    if participant.composite_score is not None:
        payload["composite_score"] = participant.composite_score
    if participant.score_breakdown is not None:
        payload["score_breakdown"] = participant.score_breakdown
    return payload


def _build_diagnostics_participant_payload(participant: ArenaParticipantResult) -> dict[str, Any]:
    """Возвращает diagnostics-часть участника (stage-агрегаты и failure-сигналы)."""

    return {
        "participant_id": participant.participant_id,
        "signals": participant.diagnostic_signals or {"summary": {}, "stage_aggregates": []},
    }
