"""Unit-тесты oracle-правил проверки expected-контракта."""

from __future__ import annotations

import pytest

from optimizer.evaluation.dataset_schema import GoldenDatasetRecord
from optimizer.evaluation.oracle_rules import evaluate_record_against_payload, is_case_passed


def _record(expected: dict) -> GoldenDatasetRecord:
    """Создает минимальную запись датасета для unit-проверок oracle правил."""

    return GoldenDatasetRecord(case_id="c1", input={"query": "x"}, expected=expected)


@pytest.mark.unit
def test_oracle_rules_pass_for_required_and_forbidden_constraints() -> None:
    """Проверяет pass-кейс: must_include найден, forbidden отсутствует."""

    record = _record({"must_include": ["hello"], "forbidden": ["spam"]})
    results = evaluate_record_against_payload(record, {"text": "hello world"})
    assert is_case_passed(results) is True


@pytest.mark.unit
def test_oracle_rules_fail_when_must_include_is_missing() -> None:
    """Проверяет fail-кейс: обязательная фраза отсутствует в output."""

    record = _record({"must_include": ["required"], "forbidden": []})
    results = evaluate_record_against_payload(record, {"text": "other"})
    assert is_case_passed(results) is False


@pytest.mark.unit
def test_oracle_rules_fail_when_forbidden_phrase_present() -> None:
    """Проверяет fail-кейс: запрещенная фраза обнаружена в output."""

    record = _record({"must_include": [], "forbidden": ["bad"]})
    results = evaluate_record_against_payload(record, {"text": "this is bad output"})
    assert is_case_passed(results) is False

