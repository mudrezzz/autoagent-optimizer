"""Исполнитель узлов Graph IR в runtime workflow."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Callable

from framework.models.interfaces import IChatModelGateway

from optimizer.graph_ir.models import GraphIRNode, GraphNodeKind
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState

NodeCallable = Callable[[RenderedGraphState, GraphIRNode], Any]


@dataclass
class NodeExecutionContext:
    """Контекст исполнения узлов: внешние зависимости и конфиги."""

    llm_gateway: IChatModelGateway | None = None
    prompt_templates: dict[str, str] = field(default_factory=dict)
    deterministic_registry: dict[str, NodeCallable] = field(default_factory=dict)
    tool_registry: dict[str, NodeCallable] = field(default_factory=dict)
    validator_registry: dict[str, NodeCallable] = field(default_factory=dict)
    hitl_registry: dict[str, NodeCallable] = field(default_factory=dict)


class GraphIRNodeExecutor:
    """Унифицированный исполнитель узлов разных типов для Graph IR."""

    def __init__(self, context: NodeExecutionContext) -> None:
        """Инициализирует исполнитель узлов с заданным контекстом зависимостей."""

        self._context = context

    def execute_node(self, node: GraphIRNode, state: RenderedGraphState) -> Any:
        """Исполняет узел и возвращает результат выполнения."""

        if node.kind == GraphNodeKind.LLM:
            return self._execute_llm(node, state)
        if node.kind == GraphNodeKind.DETERMINISTIC:
            return self._execute_with_registry(node, state, self._context.deterministic_registry)
        if node.kind == GraphNodeKind.TOOL:
            return self._execute_with_registry(node, state, self._context.tool_registry, allow_mcp_stub=True)
        if node.kind == GraphNodeKind.VALIDATOR:
            return self._execute_validator(node, state)
        if node.kind == GraphNodeKind.HITL_GATE:
            return self._execute_with_registry(node, state, self._context.hitl_registry, allow_default_hitl=True)
        raise ValueError(f"Неподдерживаемый тип узла: {node.kind.value}")

    def _execute_llm(self, node: GraphIRNode, state: RenderedGraphState) -> dict[str, Any]:
        """Выполняет LLM-узел через gateway и возвращает текстовый результат."""

        prompt = self._build_prompt(node, state)
        if self._context.llm_gateway is None:
            # В I2.S1 без API-ключа работаем в mock-режиме, чтобы demo оставался исполняемым локально.
            return {"text": f"[mock-llm] {prompt}"}
        response_text = self._context.llm_gateway.generate(prompt, metadata={"temperature": 0.2})
        return {"text": response_text}

    def _build_prompt(self, node: GraphIRNode, state: RenderedGraphState) -> str:
        """Собирает prompt для LLM-узла из шаблона и пользовательского payload."""

        prompt_id = node.config.get("prompt_id")
        template = None
        if isinstance(prompt_id, str):
            template = self._context.prompt_templates.get(prompt_id)
        if template:
            return template.format_map(_SafeDict(state.payload))
        if "query" in state.payload:
            return str(state.payload["query"])
        return (
            "Сформируй полезный ответ на основе входного payload.\n"
            f"payload={state.payload}"
        )

    def _execute_with_registry(
        self,
        node: GraphIRNode,
        state: RenderedGraphState,
        registry: dict[str, NodeCallable],
        *,
        allow_mcp_stub: bool = False,
        allow_default_hitl: bool = False,
    ) -> Any:
        """Исполняет узел через registry или импортируемый python callable."""

        component_ref = node.component_ref
        if component_ref in registry:
            return registry[component_ref](state, node)

        if component_ref.startswith("python://"):
            callable_obj = self._load_python_callable(component_ref)
            return callable_obj(state, node)

        if allow_mcp_stub and component_ref.startswith("mcp://"):
            # В I2.S1 внешние MCP-вызовы пока заглушаются, чтобы сохранить исполняемое демо локально.
            return {"status": "mcp_stub", "component_ref": component_ref}

        if allow_default_hitl:
            decision = state.payload.get("review_decision", "approve")
            return {"review_decision": decision}

        raise RuntimeError(f"Не найден executor для component_ref: {component_ref}")

    def _execute_validator(self, node: GraphIRNode, state: RenderedGraphState) -> dict[str, Any]:
        """Исполняет validator-узел и проверяет, что результат успешен."""

        result = self._execute_with_registry(node, state, self._context.validator_registry)
        if isinstance(result, bool):
            if not result:
                raise ValueError(f"Validator `{node.id}` вернул `False`.")
            return {"valid": True}
        if isinstance(result, dict):
            if result.get("valid") is False:
                raise ValueError(f"Validator `{node.id}` вернул `valid=False`.")
            return result
        return {"valid": True, "raw": result}

    def _load_python_callable(self, component_ref: str) -> NodeCallable:
        """Загружает python callable из ref вида `python://module.submodule:function`."""

        raw = component_ref[len("python://") :]
        if ":" not in raw:
            raise ValueError(f"Некорректный python component_ref: {component_ref}")
        module_name, func_name = raw.split(":", 1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name, None)
        if func is None or not callable(func):
            raise ValueError(f"Функция `{func_name}` не найдена в модуле `{module_name}`.")
        return func


class _SafeDict(dict):
    """Безопасный dict для шаблонов prompt с отсутствующими ключами."""

    def __missing__(self, key: str) -> str:
        """Возвращает placeholder, если ключ отсутствует в payload."""

        return "{" + key + "}"
