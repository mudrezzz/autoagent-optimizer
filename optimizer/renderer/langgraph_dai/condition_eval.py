"""Оценка условных выражений для переходов Graph IR."""

from __future__ import annotations

from typing import Any

from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState


class ConditionEvaluator:
    """Компонент оценки условий перехода вида `key == value` или `key != value`."""

    def evaluate(self, condition: str | None, state: RenderedGraphState) -> bool:
        """Возвращает `True`, если условие отсутствует или выражение истинно."""

        if condition is None:
            return True
        expression = condition.strip()
        if not expression:
            return True

        if "==" in expression:
            left, right = expression.split("==", 1)
            left_value = self._resolve_variable(left.strip(), state)
            right_value = self._parse_literal(right.strip())
            return left_value == right_value

        if "!=" in expression:
            left, right = expression.split("!=", 1)
            left_value = self._resolve_variable(left.strip(), state)
            right_value = self._parse_literal(right.strip())
            return left_value != right_value

        # Для v0 неизвестные форматы считаем ложными, чтобы не выполнять случайные ветки.
        return False

    def _resolve_variable(self, key: str, state: RenderedGraphState) -> Any:
        """Разрешает переменную в payload/task_context/node_outputs."""

        if key in state.payload:
            return state.payload[key]
        if key in state.task_context:
            return state.task_context[key]
        if key in state.node_outputs:
            return state.node_outputs[key]
        return None

    def _parse_literal(self, raw: str) -> Any:
        """Парсит простой литерал условия в примитив Python."""

        value = raw.strip()
        if value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1]
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            return value[1:-1]
        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

