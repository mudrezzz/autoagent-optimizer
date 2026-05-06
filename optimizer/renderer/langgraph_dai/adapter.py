"""Адаптер рендера Graph IR в исполняемый workflow на базе langgraph-dai."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from infra.openrouter.chat_gateway import OpenRouterChatModelGateway
from langgraph.checkpoint.memory import InMemorySaver

from optimizer.graph_ir.models import GraphIRSpec
from optimizer.renderer.langgraph_dai.checkpoint_store import FileRuntimeCheckpointStore, RuntimeCheckpointStoreError
from optimizer.renderer.langgraph_dai.node_executor import (
    GraphIRNodeExecutor,
    NodeCallable,
    NodeExecutionContext,
)
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState
from optimizer.renderer.langgraph_dai.workflow import RenderedGraphIRWorkflow
from optimizer.tracing.trace_store import InMemoryTraceStore


@dataclass
class RendererBindings:
    """Набор биндингов исполнителей для узлов разных типов."""

    prompt_templates: dict[str, str] = field(default_factory=dict)
    deterministic_registry: dict[str, NodeCallable] = field(default_factory=dict)
    tool_registry: dict[str, NodeCallable] = field(default_factory=dict)
    validator_registry: dict[str, NodeCallable] = field(default_factory=dict)
    hitl_registry: dict[str, NodeCallable] = field(default_factory=dict)


@dataclass
class RenderedWorkflowRuntime:
    """Контейнер рендеренного workflow и API invoke/resume/checkpoint."""

    workflow: RenderedGraphIRWorkflow
    graph_ir: GraphIRSpec
    checkpoint_store: FileRuntimeCheckpointStore | None = None

    def invoke(
        self,
        payload: dict[str, Any],
        *,
        task_id: str = "demo-task",
        run_id: str | None = None,
    ) -> RenderedGraphState:
        """Запускает workflow, сохраняет checkpoint и возвращает финальное состояние."""

        resolved_task_id = _validate_task_id(task_id)
        resolved_run_id = run_id or f"run-{uuid4()}"
        initial_state = RenderedGraphState(
            payload=dict(payload),
            task_context={"task_id": resolved_task_id, "run_id": resolved_run_id},
            active_nodes=[self.graph_ir.entry_node],
        )
        result_state = self.workflow.invoke(initial_state)
        self._save_checkpoint(resolved_task_id, result_state)
        return result_state

    def resume(
        self,
        *,
        task_id: str,
        payload_patch: dict[str, Any] | None = None,
        run_id: str | None = None,
    ) -> RenderedGraphState:
        """Возобновляет workflow из checkpoint по task_id с optional payload patch."""

        resolved_task_id = _validate_task_id(task_id)
        if self.checkpoint_store is None:
            raise RuntimeCheckpointStoreError("Resume недоступен: checkpoint_store не настроен.")

        checkpoint_state = self.checkpoint_store.load(resolved_task_id)
        merged_payload = dict(checkpoint_state.payload)
        merged_payload.update(payload_patch or {})
        merged_task_context = dict(checkpoint_state.task_context)
        merged_task_context["task_id"] = resolved_task_id
        merged_task_context["run_id"] = run_id or str(merged_task_context.get("run_id") or f"run-{uuid4()}")

        resume_state = checkpoint_state.model_copy(
            update={
                "payload": merged_payload,
                "task_context": merged_task_context,
            }
        )
        result_state = self.workflow.resume(resume_state)
        self._save_checkpoint(resolved_task_id, result_state)
        return result_state

    def _save_checkpoint(self, task_id: str, state: RenderedGraphState) -> None:
        """Сохраняет checkpoint состояния, если хранилище настроено."""

        if self.checkpoint_store is None:
            return
        self.checkpoint_store.save(task_id, state)


class GraphIRToLangGraphRenderer:
    """Рендерер, который превращает Graph IR в исполняемый BaseWorkflow."""

    def render(
        self,
        graph_ir: GraphIRSpec,
        *,
        bindings: RendererBindings | None = None,
        checkpoint_store: FileRuntimeCheckpointStore | None = None,
        enable_langgraph_checkpointer: bool = True,
    ) -> RenderedWorkflowRuntime:
        """Собирает исполняемый workflow для переданного Graph IR."""

        resolved_bindings = bindings or RendererBindings()
        llm_gateway = self._build_llm_gateway_if_available()
        context = NodeExecutionContext(
            llm_gateway=llm_gateway,
            prompt_templates=resolved_bindings.prompt_templates,
            deterministic_registry=resolved_bindings.deterministic_registry,
            tool_registry=resolved_bindings.tool_registry,
            validator_registry=resolved_bindings.validator_registry,
            hitl_registry=resolved_bindings.hitl_registry,
        )
        node_executor = GraphIRNodeExecutor(context=context)
        checkpointer = InMemorySaver() if enable_langgraph_checkpointer else None
        workflow = RenderedGraphIRWorkflow(
            graph_ir=graph_ir,
            node_executor=node_executor,
            checkpointer=checkpointer,
            trace_store=InMemoryTraceStore(),
            use_langgraph_runtime=True,
        )
        return RenderedWorkflowRuntime(
            workflow=workflow,
            graph_ir=graph_ir,
            checkpoint_store=checkpoint_store,
        )

    def _build_llm_gateway_if_available(self) -> OpenRouterChatModelGateway | None:
        """Создает gateway OpenRouter, если в окружении есть API-ключ."""

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            return None
        model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip() or "openai/gpt-4o-mini"
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip() or "https://openrouter.ai/api/v1"
        return OpenRouterChatModelGateway(api_key=api_key, model_name=model_name, base_url=base_url)


def _validate_task_id(task_id: str) -> str:
    """Проверяет, что task_id непустой для invoke/resume контрактов."""

    resolved = str(task_id).strip()
    if not resolved:
        raise RuntimeCheckpointStoreError("task_id обязателен для invoke/resume.")
    return resolved

