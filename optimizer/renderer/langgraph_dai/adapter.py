"""Адаптер рендера Graph IR в исполняемый workflow на базе langgraph-dai."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable

from infra.openrouter.chat_gateway import OpenRouterChatModelGateway

from optimizer.graph_ir.models import GraphIRSpec
from optimizer.renderer.langgraph_dai.node_executor import (
    GraphIRNodeExecutor,
    NodeCallable,
    NodeExecutionContext,
)
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState
from optimizer.renderer.langgraph_dai.workflow import RenderedGraphIRWorkflow


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
    """Контейнер рендеренного workflow и удобного invoke API."""

    workflow: RenderedGraphIRWorkflow
    graph_ir: GraphIRSpec

    def invoke(self, payload: dict[str, Any], *, task_id: str = "demo-task") -> RenderedGraphState:
        """Запускает workflow с входным payload и возвращает финальное состояние."""

        initial_state = RenderedGraphState(
            payload=dict(payload),
            task_context={"task_id": task_id},
            active_nodes=[self.graph_ir.entry_node],
        )
        result_state = self.workflow.invoke(initial_state)
        return result_state


class GraphIRToLangGraphRenderer:
    """Рендерер, который превращает Graph IR в исполняемый BaseWorkflow."""

    def render(self, graph_ir: GraphIRSpec, *, bindings: RendererBindings | None = None) -> RenderedWorkflowRuntime:
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
        workflow = RenderedGraphIRWorkflow(graph_ir=graph_ir, node_executor=node_executor, use_langgraph_runtime=True)
        return RenderedWorkflowRuntime(workflow=workflow, graph_ir=graph_ir)

    def _build_llm_gateway_if_available(self) -> OpenRouterChatModelGateway | None:
        """Создает gateway OpenRouter, если в окружении есть API-ключ."""

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            return None
        model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip() or "openai/gpt-4o-mini"
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip() or "https://openrouter.ai/api/v1"
        return OpenRouterChatModelGateway(api_key=api_key, model_name=model_name, base_url=base_url)

