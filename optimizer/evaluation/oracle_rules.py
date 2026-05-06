"""Базовые oracle-правила проверки результатов against expected контракт."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from optimizer.evaluation.dataset_schema import GoldenDatasetRecord


@dataclass(frozen=True)
class OracleRuleResult:
    """Результат применения одного oracle-правила к кейсу."""

    passed: bool
    message: str


def evaluate_record_against_payload(record: GoldenDatasetRecord, payload: dict[str, Any]) -> list[OracleRuleResult]:
    """Применяет v0-набор правил (`must_include`, `forbidden`) к output payload."""

    output_text = _extract_output_text(payload).lower()
    expected = record.expected
    must_include = _normalize_list(expected.get("must_include"))
    forbidden = _normalize_list(expected.get("forbidden"))

    results: list[OracleRuleResult] = []
    for phrase in must_include:
        phrase_lc = phrase.lower()
        passed = phrase_lc in output_text
        results.append(
            OracleRuleResult(
                passed=passed,
                message=f"must_include `{phrase}` {'найдено' if passed else 'не найдено'}",
            )
        )

    for phrase in forbidden:
        phrase_lc = phrase.lower()
        passed = phrase_lc not in output_text
        results.append(
            OracleRuleResult(
                passed=passed,
                message=f"forbidden `{phrase}` {'отсутствует' if passed else 'обнаружено'}",
            )
        )

    # Если в expected нет правил, считаем кейс неполным для oracle v0.
    if not must_include and not forbidden:
        results.append(
            OracleRuleResult(
                passed=False,
                message="expected не содержит `must_include`/`forbidden` правил для oracle v0.",
            )
        )

    return results


def is_case_passed(rule_results: list[OracleRuleResult]) -> bool:
    """Возвращает итоговый статус кейса: passed, если все правила passed."""

    return all(result.passed for result in rule_results)


def _extract_output_text(payload: dict[str, Any]) -> str:
    """Извлекает текст ответа из payload по приоритетным полям."""

    if "text" in payload and isinstance(payload["text"], str):
        return payload["text"]

    node_outputs = payload.get("node_outputs")
    if isinstance(node_outputs, dict):
        for value in node_outputs.values():
            if isinstance(value, dict):
                text_value = value.get("text")
                if isinstance(text_value, str):
                    return text_value

    return str(payload)


def _normalize_list(value: Any) -> list[str]:
    """Нормализует expected-поле в список строк (игнорируя нестроковые элементы)."""

    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]

