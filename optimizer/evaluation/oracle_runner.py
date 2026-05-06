"""Executable oracle-runner для deterministic проверки кейсов golden dataset."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from optimizer.evaluation.dataset_schema import GoldenDatasetRecord
from optimizer.evaluation.oracle_rules import OracleRuleResult, evaluate_record_against_payload, is_case_passed

OracleExecutionFn = Callable[[GoldenDatasetRecord], dict[str, Any]]


@dataclass
class OracleCaseResult:
    """Результат oracle-проверки одного кейса."""

    case_id: str
    passed: bool
    rule_results: list[OracleRuleResult]
    output_payload: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        """Преобразует результат кейса в JSON-совместимую структуру."""

        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "rule_results": [{"passed": r.passed, "message": r.message} for r in self.rule_results],
            "output_payload": self.output_payload,
        }


@dataclass
class OracleRunResult:
    """Итоговый результат прогона oracle на наборе кейсов."""

    cases_total: int
    passed: int
    failed: int
    pass_rate: float
    results: list[OracleCaseResult] = field(default_factory=list)

    def summary_payload(self) -> dict[str, Any]:
        """Возвращает JSON-совместимую сводку для CLI и smoke."""

        return {
            "cases_total": self.cases_total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
        }

    def full_payload(self) -> dict[str, Any]:
        """Возвращает полный JSON-совместимый отчет прогона."""

        return {
            **self.summary_payload(),
            "results": [result.to_payload() for result in self.results],
        }


class OracleRunner:
    """Runner, который исполняет кейсы и применяет oracle-правила v0."""

    def run(self, records: list[GoldenDatasetRecord], execute_fn: OracleExecutionFn) -> OracleRunResult:
        """Выполняет oracle-прогон по списку записей и функции исполнения."""

        case_results: list[OracleCaseResult] = []
        for record in records:
            output_payload = execute_fn(record)
            rule_results = evaluate_record_against_payload(record, output_payload)
            passed = is_case_passed(rule_results)
            case_results.append(
                OracleCaseResult(
                    case_id=record.case_id,
                    passed=passed,
                    rule_results=rule_results,
                    output_payload=output_payload,
                )
            )

        cases_total = len(case_results)
        passed_total = sum(1 for result in case_results if result.passed)
        failed_total = cases_total - passed_total
        pass_rate = float(passed_total / cases_total) if cases_total else 0.0
        return OracleRunResult(
            cases_total=cases_total,
            passed=passed_total,
            failed=failed_total,
            pass_rate=pass_rate,
            results=case_results,
        )
