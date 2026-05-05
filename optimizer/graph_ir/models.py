"""Typed-модели Graph IR v0."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from optimizer.graph_ir.validators import validate_graph_ir


class GraphNodeKind(str, Enum):
    """Поддерживаемые типы узлов в runtime-neutral Graph IR."""

    LLM = "llm"
    DETERMINISTIC = "deterministic"
    TOOL = "tool"
    VALIDATOR = "validator"
    HITL_GATE = "hitl_gate"


class GraphIRNode(BaseModel):
    """Описание узла Graph IR без привязки к конкретному runtime."""

    id: str = Field(..., min_length=1, description="Уникальный идентификатор узла.")
    kind: GraphNodeKind = Field(..., description="Тип узла.")
    component_ref: str = Field(..., min_length=1, description="Ссылка на компонент реализации.")
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Параметры узла в нейтральном представлении.",
    )
    on_fail: Literal["stop", "retry", "fallback"] = Field(
        default="stop",
        description="Политика обработки ошибки узла.",
    )


class GraphIREdge(BaseModel):
    """Описание ребра между узлами Graph IR."""

    source: str = Field(..., min_length=1, description="Идентификатор исходного узла.")
    target: str = Field(..., min_length=1, description="Идентификатор целевого узла.")
    condition: str | None = Field(
        default=None,
        description="Условие перехода (runtime-neutral строковое выражение).",
    )
    label: str | None = Field(default=None, description="Человекочитаемая подпись ребра.")


class GraphIRSpec(BaseModel):
    """Корневая модель Graph IR v0."""

    ir_version: Literal["0.1"] = Field(..., description="Версия схемы Graph IR.")
    entry_node: str = Field(..., min_length=1, description="Стартовый узел графа.")
    terminal_nodes: list[str] = Field(
        ...,
        min_length=1,
        description="Список завершающих узлов графа.",
    )
    nodes: list[GraphIRNode] = Field(..., min_length=1, description="Список узлов.")
    edges: list[GraphIREdge] = Field(..., min_length=1, description="Список ребер.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительные метаданные графа.",
    )

    @model_validator(mode="after")
    def validate_integrity(self) -> "GraphIRSpec":
        """Запускает полный набор проверок целостности Graph IR."""

        validate_graph_ir(self)
        return self

    def summary(self) -> dict[str, int | str]:
        """Возвращает краткую сводку для логов и smoke-проверок."""

        return {
            "ir_version": self.ir_version,
            "entry_node": self.entry_node,
            "terminal_nodes": len(self.terminal_nodes),
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }

