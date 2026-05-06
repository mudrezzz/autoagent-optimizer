"""Тестовые callback-функции для интеграционных сценариев рендерера."""

from __future__ import annotations

from optimizer.graph_ir.models import GraphIRNode
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState


def route_node(state: RenderedGraphState, _node: GraphIRNode) -> dict:
    """Маршрутизатор риска для тестового branch-сценария."""

    action_risk = state.payload.get("action_risk", "low")
    return {"action_risk": action_risk}


def always_valid(_state: RenderedGraphState, _node: GraphIRNode) -> dict:
    """Упрощенный validator для тестовых сценариев."""

    return {"valid": True}

