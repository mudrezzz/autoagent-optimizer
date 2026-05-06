"""Integration-тесты runtime-рендерера Graph IR."""

from __future__ import annotations

from pathlib import Path

from optimizer.graph_ir.models import GraphIREdge, GraphIRNode, GraphIRSpec, GraphNodeKind
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer, RendererBindings
from optimizer.renderer.langgraph_dai.checkpoint_store import FileRuntimeCheckpointStore, RuntimeCheckpointStoreError
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
    assert result.trace_summary["task_id"] == "it-low-risk"
    assert result.trace_summary["run_id"]
    assert result.trace_summary["events_total"] >= len(result.executed_nodes)
    assert any(event["status"] == "started" for event in result.node_events)
    assert any(event["status"] == "completed" for event in result.node_events)


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
    assert result.trace_summary["task_id"] == "it-high-risk"
    assert result.trace_summary["started"] >= 1


@pytest.mark.integration
def test_renderer_resume_from_checkpoint_preserves_task_id(tmp_path: Path) -> None:
    """Проверяет invoke->resume путь с checkpoint и сохранением task_id контекста."""

    graph_ir = _build_conditional_graph_ir()
    checkpoint_store = FileRuntimeCheckpointStore(tmp_path / "checkpoints")
    renderer = GraphIRToLangGraphRenderer()
    runtime = renderer.render(
        graph_ir,
        bindings=RendererBindings(),
        checkpoint_store=checkpoint_store,
    )

    first_state = runtime.invoke(payload={"action_risk": "low"}, task_id="resume-contract-task")
    assert checkpoint_store.exists("resume-contract-task") is True

    resumed_state = runtime.resume(
        task_id="resume-contract-task",
        payload_patch={"action_risk": "high", "review_decision": "approve"},
    )
    assert resumed_state.task_context["task_id"] == "resume-contract-task"
    assert resumed_state.trace_summary["task_id"] == "resume-contract-task"
    assert len(resumed_state.executed_nodes) >= len(first_state.executed_nodes)


@pytest.mark.integration
def test_renderer_resume_fails_for_missing_or_empty_task_id(tmp_path: Path) -> None:
    """Проверяет негативные кейсы resume: пустой task_id и отсутствующий checkpoint."""

    graph_ir = _build_conditional_graph_ir()
    checkpoint_store = FileRuntimeCheckpointStore(tmp_path / "checkpoints")
    renderer = GraphIRToLangGraphRenderer()
    runtime = renderer.render(
        graph_ir,
        bindings=RendererBindings(),
        checkpoint_store=checkpoint_store,
    )

    with pytest.raises(RuntimeCheckpointStoreError):
        runtime.resume(task_id="")

    with pytest.raises(RuntimeCheckpointStoreError):
        runtime.resume(task_id="unknown-task")

    with pytest.raises(RuntimeCheckpointStoreError):
        runtime.invoke(payload={"action_risk": "low"}, task_id="")
