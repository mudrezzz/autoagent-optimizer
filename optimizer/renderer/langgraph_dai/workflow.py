"""Исполняемый workflow, собранный из Graph IR поверх BaseWorkflow."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from framework.workflows.base import BaseWorkflow, WorkflowExecutionContext, WorkflowNodeSpec

from optimizer.graph_ir.models import GraphIREdge, GraphIRNode, GraphIRSpec
from optimizer.renderer.langgraph_dai.condition_eval import ConditionEvaluator
from optimizer.renderer.langgraph_dai.node_executor import GraphIRNodeExecutor
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState
from optimizer.tracing.node_events import NodeEventStatus, NodeExecutionEvent, utc_now_iso
from optimizer.tracing.trace_store import InMemoryTraceStore


class RenderedGraphIRWorkflow(BaseWorkflow):
    """Workflow-адаптер, который исполняет Graph IR в рамках BaseWorkflow."""

    def __init__(
        self,
        graph_ir: GraphIRSpec,
        node_executor: GraphIRNodeExecutor,
        *,
        checkpointer: object | None = None,
        trace_store: InMemoryTraceStore | None = None,
        use_langgraph_runtime: bool = True,
    ) -> None:
        """Инициализирует workflow по Graph IR и компилирует invoke/resume графы."""

        self._graph_ir = graph_ir
        self._node_executor = node_executor
        self._condition_evaluator = ConditionEvaluator()
        self._trace_store = trace_store or InMemoryTraceStore()
        self._nodes_by_id: dict[str, GraphIRNode] = {node.id: node for node in graph_ir.nodes}
        self._edges_by_source: dict[str, list[GraphIREdge]] = defaultdict(list)
        for edge in graph_ir.edges:
            self._edges_by_source[edge.source].append(edge)
        self._topological_order = self._build_topological_order(graph_ir)

        super().__init__(use_langgraph_runtime=use_langgraph_runtime, checkpointer=checkpointer)
        self.compile()

    def state_schema(self) -> type[RenderedGraphState]:
        """Возвращает тип состояния workflow."""

        return RenderedGraphState

    def workflow_nodes(self, *, is_resume: bool) -> list[WorkflowNodeSpec]:
        """Возвращает линейный список node specs в топологическом порядке."""

        _ = is_resume
        specs: list[WorkflowNodeSpec] = []
        for node_id in self._topological_order:
            specs.append(WorkflowNodeSpec(name=node_id, handler=self._build_node_handler(node_id)))
        return specs

    def _build_node_handler(self, node_id: str):
        """Создает handler исполнения для конкретного узла Graph IR."""

        def _handler(state: RenderedGraphState, context: WorkflowExecutionContext) -> RenderedGraphState:
            _ = context
            return self._execute_graph_node(node_id=node_id, state=state)

        return _handler

    def _execute_graph_node(self, *, node_id: str, state: RenderedGraphState) -> RenderedGraphState:
        """Исполняет узел, если он активен, и продвигает фронт активных узлов."""

        active_set = set(state.active_nodes)
        if not active_set:
            active_set.add(self._graph_ir.entry_node)

        if node_id not in active_set:
            self._record_event(state, node_id=node_id, status=NodeEventStatus.SKIPPED)
            skipped_nodes = list(state.skipped_nodes)
            skipped_nodes.append(node_id)
            trace = list(state.trace)
            trace.append({"node_id": node_id, "status": "skipped"})
            return state.model_copy(
                update={
                    "skipped_nodes": skipped_nodes,
                    "trace": trace,
                    "node_events": self._render_node_events(state),
                    "trace_summary": self._render_trace_summary(state),
                }
            )

        node = self._nodes_by_id[node_id]
        self._record_event(state, node_id=node_id, status=NodeEventStatus.STARTED)
        node_outputs = dict(state.node_outputs)
        payload = dict(state.payload)
        errors = list(state.errors)
        trace = list(state.trace)

        # Удаляем текущий узел из активных перед выполнением.
        active_set.remove(node_id)

        try:
            output = self._execute_with_policy(node=node, state=state)
            node_outputs[node_id] = output
            if isinstance(output, dict):
                payload.update(output)
            status = "completed"
            self._record_event(state, node_id=node_id, status=NodeEventStatus.COMPLETED)
        except Exception as exc:
            errors.append(f"{node_id}: {exc}")
            status = "failed"
            self._record_event(state, node_id=node_id, status=NodeEventStatus.FAILED, error=str(exc))
            if node.on_fail == "fallback":
                fallback_output = {"status": "fallback", "error": str(exc)}
                node_outputs[node_id] = fallback_output
                payload.update(fallback_output)
                status = "fallback"
            else:
                # Для `stop` и окончательного `retry` пробрасываем ошибку наверх.
                trace.append({"node_id": node_id, "status": status, "error": str(exc)})
                raise

        next_nodes = self._resolve_next_nodes(
            node_id=node_id,
            state=state.model_copy(update={"payload": payload, "node_outputs": node_outputs}),
        )
        active_set.update(next_nodes)

        executed_nodes = list(state.executed_nodes)
        executed_nodes.append(node_id)
        trace.append({"node_id": node_id, "status": status, "next_nodes": sorted(next_nodes)})

        return state.model_copy(
            update={
                "payload": payload,
                "active_nodes": sorted(active_set),
                "executed_nodes": executed_nodes,
                "node_outputs": node_outputs,
                "trace": trace,
                "errors": errors,
                "node_events": self._render_node_events(state),
                "trace_summary": self._render_trace_summary(state),
            }
        )

    def _execute_with_policy(self, *, node: GraphIRNode, state: RenderedGraphState) -> Any:
        """Исполняет узел с учетом политики `on_fail`."""

        if node.on_fail != "retry":
            return self._node_executor.execute_node(node, state)

        # Для retry в I2.S1+ делаем одну повторную попытку.
        first_error: Exception | None = None
        for _attempt in (1, 2):
            try:
                return self._node_executor.execute_node(node, state)
            except Exception as exc:  # pragma: no cover - подтверждается интеграционными тестами.
                if first_error is None:
                    first_error = exc
                continue
        assert first_error is not None
        raise first_error

    def _resolve_next_nodes(self, *, node_id: str, state: RenderedGraphState) -> set[str]:
        """Определяет следующую активную группу узлов с учетом edge-условий."""

        next_nodes: set[str] = set()
        for edge in self._edges_by_source.get(node_id, []):
            if self._condition_evaluator.evaluate(edge.condition, state):
                next_nodes.add(edge.target)
        return next_nodes

    def _build_topological_order(self, graph_ir: GraphIRSpec) -> list[str]:
        """Строит топологический порядок узлов и валидирует отсутствие циклов."""

        incoming_count: dict[str, int] = {node.id: 0 for node in graph_ir.nodes}
        adjacency: dict[str, list[str]] = defaultdict(list)
        for edge in graph_ir.edges:
            incoming_count[edge.target] += 1
            adjacency[edge.source].append(edge.target)

        queue: deque[str] = deque(sorted([node_id for node_id, count in incoming_count.items() if count == 0]))
        order: list[str] = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for nxt in adjacency.get(current, []):
                incoming_count[nxt] -= 1
                if incoming_count[nxt] == 0:
                    queue.append(nxt)

        if len(order) != len(graph_ir.nodes):
            raise ValueError("Graph IR содержит цикл; циклические графы в I2 не поддерживаются.")
        return order

    def _record_event(
        self,
        state: RenderedGraphState,
        *,
        node_id: str,
        status: NodeEventStatus,
        error: str | None = None,
    ) -> None:
        """Регистрирует node-level событие в trace store."""

        run_id, task_id = _resolve_run_context(state)
        event = NodeExecutionEvent(
            run_id=run_id,
            task_id=task_id,
            node_id=node_id,
            status=status,
            timestamp_utc=utc_now_iso(),
            error=error,
        )
        self._trace_store.record(event)

    def _render_node_events(self, state: RenderedGraphState) -> list[dict[str, Any]]:
        """Возвращает сериализованные события текущего run из trace store."""

        run_id, _task_id = _resolve_run_context(state)
        events = self._trace_store.get_run_events(run_id)
        return [event.to_payload() for event in events]

    def _render_trace_summary(self, state: RenderedGraphState) -> dict[str, Any]:
        """Возвращает агрегированную сводку trace для текущего run."""

        run_id, task_id = _resolve_run_context(state)
        return self._trace_store.get_run_summary(run_id=run_id, task_id=task_id)


def _resolve_run_context(state: RenderedGraphState) -> tuple[str, str]:
    """Извлекает `run_id` и `task_id` из `task_context` с безопасными fallback."""

    run_id = str(state.task_context.get("run_id", "run-unknown")).strip() or "run-unknown"
    task_id = str(state.task_context.get("task_id", "task-unknown")).strip() or "task-unknown"
    return run_id, task_id
