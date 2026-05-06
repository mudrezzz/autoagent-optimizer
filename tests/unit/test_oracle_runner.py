"""Unit-тесты oracle runner summary и подсчета pass/fail."""

from __future__ import annotations

import pytest

from optimizer.evaluation.dataset_schema import GoldenDatasetRecord
from optimizer.evaluation.oracle_runner import OracleRunner


@pytest.mark.unit
def test_oracle_runner_counts_passed_and_failed_cases() -> None:
    """Проверяет корректный подсчет passed/failed и pass_rate в runner."""

    records = [
        GoldenDatasetRecord(
            case_id="c1",
            input={"query": "q1"},
            expected={"must_include": ["alpha"], "forbidden": []},
        ),
        GoldenDatasetRecord(
            case_id="c2",
            input={"query": "q2"},
            expected={"must_include": ["beta"], "forbidden": []},
        ),
    ]

    def _execute(record: GoldenDatasetRecord) -> dict:
        if record.case_id == "c1":
            return {"text": "alpha present"}
        return {"text": "no required phrase"}

    runner = OracleRunner()
    result = runner.run(records, _execute)
    assert result.cases_total == 2
    assert result.passed == 1
    assert result.failed == 1
    assert result.pass_rate == 0.5

