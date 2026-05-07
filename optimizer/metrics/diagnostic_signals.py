"""Расчет диагностических сигналов по кейсам и стадиям пайплайна."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class StageDiagnosticAggregate:
    """Агрегированные диагностические метрики одной стадии пайплайна."""

    stage: str
    executions_total: int
    touched_failed_cases: int
    rule_failures_total: int
    avg_duration_ms: float
    bottleneck_score: float

    def to_payload(self) -> dict[str, Any]:
        """Преобразует агрегат стадии в JSON-совместимый словарь."""

        return {
            "stage": self.stage,
            "executions_total": self.executions_total,
            "touched_failed_cases": self.touched_failed_cases,
            "rule_failures_total": self.rule_failures_total,
            "avg_duration_ms": self.avg_duration_ms,
            "bottleneck_score": self.bottleneck_score,
        }


def compute_diagnostic_signals(
    oracle_report: dict[str, Any] | None,
    node_stage_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Строит диагностические сигналы `case -> stage -> aggregate` для одного участника."""

    if not isinstance(oracle_report, dict):
        return _empty_diagnostics()

    results = oracle_report.get("results")
    if not isinstance(results, list) or not results:
        return _empty_diagnostics()

    stage_map = node_stage_map or {}
    per_stage_acc: dict[str, dict[str, float | int]] = {}
    failed_cases_total = 0
    total_rule_failures = 0

    for case_result in results:
        if not isinstance(case_result, dict):
            continue

        is_failed_case = not bool(case_result.get("passed", False))
        if is_failed_case:
            failed_cases_total += 1

        output_payload = case_result.get("output_payload")
        if not isinstance(output_payload, dict):
            output_payload = {}

        executed_nodes = output_payload.get("executed_nodes")
        if not isinstance(executed_nodes, list):
            executed_nodes = []
        stages = [_stage_for_node(node_id, stage_map) for node_id in executed_nodes if isinstance(node_id, str)]
        if not stages:
            stages = ["unknown"]

        duration_ms = _extract_duration_ms(output_payload)
        case_rule_failures = _count_rule_failures(case_result.get("rule_results"))
        total_rule_failures += case_rule_failures

        for stage in set(stages):
            acc = per_stage_acc.setdefault(
                stage,
                {
                    "executions_total": 0,
                    "touched_failed_cases": 0,
                    "rule_failures_total": 0,
                    "duration_ms_total": 0.0,
                    "duration_samples": 0,
                },
            )
            acc["executions_total"] += stages.count(stage)
            if is_failed_case:
                acc["touched_failed_cases"] += 1
            acc["rule_failures_total"] += case_rule_failures
            if duration_ms is not None:
                acc["duration_ms_total"] += float(duration_ms)
                acc["duration_samples"] += 1

    cases_total = max(1, len(results))
    stage_aggregates: list[StageDiagnosticAggregate] = []
    for stage, acc in per_stage_acc.items():
        duration_samples = int(acc["duration_samples"])
        avg_duration_ms = float(acc["duration_ms_total"]) / duration_samples if duration_samples > 0 else 0.0
        prevalence = int(acc["touched_failed_cases"]) / cases_total
        impact = int(acc["rule_failures_total"]) / cases_total
        bottleneck_score = prevalence * impact
        stage_aggregates.append(
            StageDiagnosticAggregate(
                stage=stage,
                executions_total=int(acc["executions_total"]),
                touched_failed_cases=int(acc["touched_failed_cases"]),
                rule_failures_total=int(acc["rule_failures_total"]),
                avg_duration_ms=round(avg_duration_ms, 6),
                bottleneck_score=round(bottleneck_score, 6),
            )
        )

    stage_aggregates.sort(key=lambda item: item.bottleneck_score, reverse=True)
    return {
        "summary": {
            "cases_total": len(results),
            "failed_cases_total": failed_cases_total,
            "failure_rate": round(failed_cases_total / cases_total, 6),
            "rule_failures_total": total_rule_failures,
        },
        "stage_aggregates": [item.to_payload() for item in stage_aggregates],
    }


def _empty_diagnostics() -> dict[str, Any]:
    """Возвращает пустую структуру diagnostics при отсутствии данных кейсов."""

    return {
        "summary": {
            "cases_total": 0,
            "failed_cases_total": 0,
            "failure_rate": 0.0,
            "rule_failures_total": 0,
        },
        "stage_aggregates": [],
    }


def _stage_for_node(node_id: str, node_stage_map: dict[str, str]) -> str:
    """Возвращает stage-тип узла по карте node->stage с fallback в `unknown`."""

    return node_stage_map.get(node_id, "unknown")


def _extract_duration_ms(output_payload: dict[str, Any]) -> int | None:
    """Извлекает длительность кейса из `trace_summary.duration_ms` при наличии."""

    trace_summary = output_payload.get("trace_summary")
    if not isinstance(trace_summary, dict):
        return None
    duration_ms = trace_summary.get("duration_ms")
    if isinstance(duration_ms, int):
        return max(0, duration_ms)
    return None


def _count_rule_failures(rule_results: Any) -> int:
    """Считает число проваленных oracle-правил в одном кейсе."""

    if not isinstance(rule_results, list):
        return 0
    return sum(1 for item in rule_results if isinstance(item, dict) and not bool(item.get("passed", False)))

