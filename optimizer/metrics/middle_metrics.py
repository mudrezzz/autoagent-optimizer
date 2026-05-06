"""Расчет middle-метрик качества/стоимости/латентности из oracle-отчета."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class MiddleMetricsResult:
    """Агрегированный набор middle-метрик участника турнира."""

    coverage: float
    rule_violations_total: int
    nodes_executed_total: int
    avg_nodes_per_case: float
    llm_calls_total: int
    duration_ms_total: int
    duration_ms_avg: float
    p95_case_duration_ms: float

    def to_payload(self) -> dict[str, float | int]:
        """Преобразует middle-метрики в JSON-совместимый словарь."""

        return {
            "coverage": self.coverage,
            "rule_violations_total": self.rule_violations_total,
            "nodes_executed_total": self.nodes_executed_total,
            "avg_nodes_per_case": self.avg_nodes_per_case,
            "llm_calls_total": self.llm_calls_total,
            "duration_ms_total": self.duration_ms_total,
            "duration_ms_avg": self.duration_ms_avg,
            "p95_case_duration_ms": self.p95_case_duration_ms,
        }


def compute_middle_metrics(oracle_report: dict[str, Any] | None) -> MiddleMetricsResult:
    """Вычисляет middle-метрики участника из детального oracle-отчета."""

    if not isinstance(oracle_report, dict):
        return _empty_middle_metrics()

    results = oracle_report.get("results")
    if not isinstance(results, list) or not results:
        return _empty_middle_metrics()

    covered_cases = 0
    rule_violations_total = 0
    nodes_executed_total = 0
    llm_calls_total = 0
    durations_ms: list[int] = []

    for case_result in results:
        if not isinstance(case_result, dict):
            continue
        output_payload = case_result.get("output_payload")
        if not isinstance(output_payload, dict):
            output_payload = {}

        if _has_output_text(output_payload):
            covered_cases += 1

        rule_results = case_result.get("rule_results")
        if isinstance(rule_results, list):
            rule_violations_total += sum(1 for rule in rule_results if isinstance(rule, dict) and not rule.get("passed", False))

        nodes_executed_total += _extract_nodes_executed(output_payload)
        llm_calls_total += _extract_llm_calls(output_payload)

        duration_ms = _extract_duration_ms(output_payload)
        if duration_ms is not None:
            durations_ms.append(duration_ms)

    cases_total = max(1, len(results))
    coverage = covered_cases / cases_total
    avg_nodes_per_case = nodes_executed_total / cases_total
    duration_ms_total = sum(durations_ms)
    duration_ms_avg = duration_ms_total / cases_total
    p95_case_duration_ms = _p95(durations_ms)

    return MiddleMetricsResult(
        coverage=coverage,
        rule_violations_total=rule_violations_total,
        nodes_executed_total=nodes_executed_total,
        avg_nodes_per_case=avg_nodes_per_case,
        llm_calls_total=llm_calls_total,
        duration_ms_total=duration_ms_total,
        duration_ms_avg=duration_ms_avg,
        p95_case_duration_ms=p95_case_duration_ms,
    )


def _empty_middle_metrics() -> MiddleMetricsResult:
    """Возвращает нулевой набор middle-метрик для пустого отчета."""

    return MiddleMetricsResult(
        coverage=0.0,
        rule_violations_total=0,
        nodes_executed_total=0,
        avg_nodes_per_case=0.0,
        llm_calls_total=0,
        duration_ms_total=0,
        duration_ms_avg=0.0,
        p95_case_duration_ms=0.0,
    )


def _has_output_text(output_payload: dict[str, Any]) -> bool:
    """Проверяет, что кейс вернул непустой текстовый ответ."""

    text = output_payload.get("text")
    return isinstance(text, str) and bool(text.strip())


def _extract_nodes_executed(output_payload: dict[str, Any]) -> int:
    """Извлекает число исполненных узлов из output payload кейса."""

    trace_summary = output_payload.get("trace_summary")
    if isinstance(trace_summary, dict):
        completed = trace_summary.get("completed")
        if isinstance(completed, int):
            return max(0, completed)

    node_outputs = output_payload.get("node_outputs")
    if isinstance(node_outputs, dict):
        return len(node_outputs)
    return 0


def _extract_llm_calls(output_payload: dict[str, Any]) -> int:
    """Извлекает число LLM-вызовов из output payload кейса."""

    llm_calls = output_payload.get("llm_calls")
    if isinstance(llm_calls, int):
        return max(0, llm_calls)
    return 0


def _extract_duration_ms(output_payload: dict[str, Any]) -> int | None:
    """Извлекает длительность кейса в миллисекундах из output payload."""

    trace_summary = output_payload.get("trace_summary")
    if isinstance(trace_summary, dict):
        duration_ms = trace_summary.get("duration_ms")
        if isinstance(duration_ms, int):
            return max(0, duration_ms)
    return None


def _p95(values: list[int]) -> float:
    """Считает p95 по списку длительностей в миллисекундах."""

    if not values:
        return 0.0
    sorted_values = sorted(values)
    percentile_index = max(0, math.ceil(0.95 * len(sorted_values)) - 1)
    return float(sorted_values[percentile_index])

