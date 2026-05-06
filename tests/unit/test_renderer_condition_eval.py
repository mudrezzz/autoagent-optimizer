"""Unit-тесты оценки branch-условий рендерера."""

from __future__ import annotations

import pytest

from optimizer.renderer.langgraph_dai.condition_eval import ConditionEvaluator
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState


@pytest.mark.unit
def test_condition_evaluator_true_for_none_condition() -> None:
    """Проверяет, что пустое условие считается истинным."""

    evaluator = ConditionEvaluator()
    state = RenderedGraphState(payload={"action_risk": "low"})
    assert evaluator.evaluate(None, state) is True


@pytest.mark.unit
def test_condition_evaluator_supports_equality_and_inequality() -> None:
    """Проверяет поддержку операторов `==` и `!=`."""

    evaluator = ConditionEvaluator()
    state = RenderedGraphState(payload={"action_risk": "high"})
    assert evaluator.evaluate("action_risk == high", state) is True
    assert evaluator.evaluate("action_risk != low", state) is True
    assert evaluator.evaluate("action_risk == low", state) is False


@pytest.mark.unit
def test_condition_evaluator_unknown_expression_returns_false() -> None:
    """Проверяет, что неподдерживаемый формат условия не активирует ветку."""

    evaluator = ConditionEvaluator()
    state = RenderedGraphState(payload={"x": 1})
    assert evaluator.evaluate("x > 0", state) is False

