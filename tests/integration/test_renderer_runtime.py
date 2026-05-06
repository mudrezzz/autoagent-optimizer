"""Integration-тесты runtime-рендерера Graph IR."""

from __future__ import annotations

from optimizer.graph_ir.models import GraphIREdge, GraphIRNode, GraphIRSpec, GraphNodeKind
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer, RendererBindings
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState

import pytest


def _build_conditional_graph_ir() -> GraphIRSpec:
    """Создает тестовый Graph IR с branch-логикой для проверки условных ребер."""

    return GraphIRSpec(
        ir_version="0.1",
        entry_node="route",
        terminal_nodes=["finish"],
        nodes=[
            GraphIRNode(
                id="route",
                kind=GraphNodeKind.DETERMINISTIC,
                component_ref="python://optimizer.renderer.langgraph_dai.test_callbacks:route_node",
                config={},
                on_fail="stop",
            ),
            GraphIRNode(
                id="need_review",
                kind=GraphNodeKind.HITL_GATE,
                component_ref="workflow://hitl/default",
                config={},
                on_fail="stop",
            ),
            GraphIRNode(
                id="execute_safe",
                kind=GraphNodeKind.TOOL,
                component_ref="mcp://support_tools/execute_safe_action",
                config={},
                on_fail="fallback",
            ),
            GraphIRNode(
                id="finish",
                kind=GraphNodeKind.VALIDATOR,
                component_ref="python://optimizer.renderer.langgraph_dai.test_callbacks:always_valid",
                config={},
                on_fail="stop",
            ),
        ],
        edges=[
            GraphIREdge(source="route", target="need_review", condition="action_risk == high"),
            GraphIREdge(source="route", target="execute_safe", condition="action_risk == low"),
            GraphIREdge(source="need_review", target="execute_safe", condition="review_decision == approve"),
            GraphIREdge(source="execute_safe", target="finish", condition=None),
        ],
        metadata={},
    )


@pytest.mark.integration
def test_renderer_executes_low_risk_branch() -> None:
    """Проверяет ветвление на low-risk путь без HITL."""

    graph_ir = _build_conditional_graph_ir()
    renderer = GraphIRToLangGraphRenderer()
    runtime = renderer.render(graph_ir, bindings=RendererBindings())

    result = runtime.invoke(payload={"action_risk": "low"}, task_id="it-low-risk")
    assert "execute_safe" in result.executed_nodes
    assert "finish" in result.executed_nodes
    assert "need_review" in result.skipped_nodes


@pytest.mark.integration
def test_renderer_executes_high_risk_branch_with_review() -> None:
    """Проверяет ветвление на high-risk путь с HITL approval."""

    graph_ir = _build_conditional_graph_ir()
    renderer = GraphIRToLangGraphRenderer()
    runtime = renderer.render(graph_ir, bindings=RendererBindings())

    result = runtime.invoke(
        payload={"action_risk": "high", "review_decision": "approve"},
        task_id="it-high-risk",
    )
    assert "need_review" in result.executed_nodes
    assert "execute_safe" in result.executed_nodes
    assert "finish" in result.executed_nodes
