"""Typed-схема DSL v0 для AutoAgent Optimizer."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class NodeType(str, Enum):
    """Перечень поддерживаемых типов узлов в DSL v0."""

    LLM = "llm"
    DETERMINISTIC = "deterministic"
    TOOL = "tool"
    VALIDATOR = "validator"
    HITL_GATE = "hitl_gate"


class ProjectMeta(BaseModel):
    """Метаданные проекта оптимизации."""

    id: str = Field(..., min_length=1, description="Уникальный идентификатор проекта.")
    name: str = Field(..., min_length=1, description="Человекочитаемое название проекта.")
    description: str = Field(..., min_length=1, description="Краткое описание задачи проекта.")


class MissionSpec(BaseModel):
    """Описание целевой бизнес-задачи и критерия успеха."""

    task_type: str = Field(..., min_length=1, description="Тип задачи, например `ocr_extraction`.")
    objective: str = Field(..., min_length=1, description="Формулировка основной цели оптимизации.")
    success_definition: str = Field(..., min_length=1, description="Определение, что считаем успешным результатом.")


class ConstraintsSpec(BaseModel):
    """Жесткие и мягкие ограничения выполнения."""

    max_cost_usd: float | None = Field(default=None, gt=0, description="Максимальная стоимость прогона в USD.")
    max_latency_ms: int | None = Field(default=None, gt=0, description="Максимальная допустимая latency в миллисекундах.")
    allowed_model_providers: list[str] = Field(
        default_factory=list,
        description="Белый список провайдеров моделей.",
    )
    require_human_approval: bool = Field(
        default=False,
        description="Требуется ли обязательный человек на финальном approval-гейте.",
    )


class DatasetSpec(BaseModel):
    """Описание датасета для оценки или оптимизации."""

    id: str = Field(..., min_length=1, description="Идентификатор датасета.")
    format: Literal["jsonl"] = Field(..., description="Формат датасета. В v0 поддерживается только jsonl.")
    path: str = Field(..., min_length=1, description="Путь до файла датасета.")
    split: Literal["train", "validation", "test"] = Field(..., description="Сплит датасета.")


class ComponentRefSpec(BaseModel):
    """Ссылка на компонент, который используется узлом графа."""

    id: str = Field(..., min_length=1, description="Идентификатор компонента.")
    kind: NodeType = Field(..., description="Тип компонента, совместимый с типом узла.")
    implementation: str = Field(..., min_length=1, description="Техническая реализация компонента (ref/uri/path).")


class NodeSpec(BaseModel):
    """Описание одного узла исполняемого графа."""

    id: str = Field(..., min_length=1, description="Уникальный идентификатор узла.")
    type: NodeType = Field(..., description="Тип узла.")
    component_id: str = Field(..., min_length=1, description="Ссылка на компонент по `components[].id`.")
    prompt_id: str | None = Field(
        default=None,
        description="Идентификатор prompt-конфига для LLM-узлов.",
    )
    on_fail: Literal["stop", "retry", "fallback"] = Field(
        default="stop",
        description="Политика обработки ошибки узла.",
    )


class EdgeSpec(BaseModel):
    """Описание ребра между узлами графа."""

    source: str = Field(..., min_length=1, description="Источник ребра.")
    target: str = Field(..., min_length=1, description="Целевой узел ребра.")
    condition: str | None = Field(
        default=None,
        description="Условие перехода. Для v0 хранится как строка.",
    )


class GraphSpec(BaseModel):
    """Декларативное описание графа workflow."""

    entry_node: str = Field(..., min_length=1, description="Стартовый узел графа.")
    nodes: list[NodeSpec] = Field(..., min_length=1, description="Список узлов графа.")
    edges: list[EdgeSpec] = Field(..., min_length=1, description="Список ребер графа.")

    @model_validator(mode="after")
    def validate_graph_integrity(self) -> "GraphSpec":
        """Проверяет целостность графа: уникальность узлов, entry и ссылки ребер."""

        node_ids = [node.id for node in self.nodes]
        unique_node_ids = set(node_ids)
        if len(unique_node_ids) != len(node_ids):
            raise ValueError("В графе обнаружены дублирующиеся `nodes[].id`.")

        if self.entry_node not in unique_node_ids:
            raise ValueError("`graph.entry_node` не найден среди `graph.nodes[].id`.")

        for edge in self.edges:
            if edge.source not in unique_node_ids:
                raise ValueError(f"Источник ребра `{edge.source}` не найден среди узлов.")
            if edge.target not in unique_node_ids:
                raise ValueError(f"Цель ребра `{edge.target}` не найдена среди узлов.")

        return self


class MetricSpec(BaseModel):
    """Описание метрики для оценки результатов и внутренних этапов."""

    id: str = Field(..., min_length=1, description="Идентификатор метрики.")
    kind: Literal["output", "middle"] = Field(..., description="Класс метрики: итоговая или промежуточная.")
    direction: Literal["maximize", "minimize"] = Field(..., description="Направление оптимизации.")
    description: str = Field(..., min_length=1, description="Человекочитаемое определение метрики.")


class BudgetSpec(BaseModel):
    """Бюджетные ограничения для optimization run."""

    max_trials: int = Field(..., gt=0, description="Максимальное количество trial-запусков.")
    max_total_cost_usd: float = Field(..., gt=0, description="Общий бюджет на запуск в USD.")
    max_wall_time_minutes: int = Field(..., gt=0, description="Лимит времени на прогон в минутах.")


class ArchitectureCandidateSpec(BaseModel):
    """Описание архитектурного кандидата для турнира."""

    id: str = Field(..., min_length=1, description="Идентификатор кандидата.")
    template: str = Field(..., min_length=1, description="Название базового шаблона архитектуры.")
    enabled: bool = Field(default=True, description="Признак участия кандидата в текущем запуске.")


class ArchitectureSpaceSpec(BaseModel):
    """Пространство архитектурных кандидатов и базовая стратегия выбора."""

    selection_policy: Literal["equal_budget_tournament"] = Field(
        default="equal_budget_tournament",
        description="Стратегия первичного сравнения кандидатов.",
    )
    candidates: list[ArchitectureCandidateSpec] = Field(
        ...,
        min_length=1,
        description="Набор архитектурных кандидатов.",
    )


class AutoAgentDslSpec(BaseModel):
    """Корневая модель DSL v0 для описания optimization-проекта."""

    schema_version: Literal["0.1"] = Field(..., description="Версия DSL-схемы.")
    project: ProjectMeta
    mission: MissionSpec
    constraints: ConstraintsSpec = Field(default_factory=ConstraintsSpec)
    datasets: list[DatasetSpec] = Field(default_factory=list)
    components: list[ComponentRefSpec] = Field(default_factory=list)
    graph: GraphSpec
    metrics: list[MetricSpec] = Field(default_factory=list)
    budget: BudgetSpec
    architecture_space: ArchitectureSpaceSpec

    @model_validator(mode="after")
    def validate_component_references(self) -> "AutoAgentDslSpec":
        """Проверяет, что узлы графа ссылаются только на существующие компоненты."""

        component_ids = {component.id for component in self.components}
        node_component_ids = {node.component_id for node in self.graph.nodes}

        missing_components = sorted(node_component_ids - component_ids)
        if missing_components:
            joined = ", ".join(missing_components)
            raise ValueError(f"Узлы графа ссылаются на отсутствующие компоненты: {joined}.")

        return self

    def summary(self) -> dict[str, int | str]:
        """Возвращает краткое резюме спецификации для CLI и smoke-проверок."""

        return {
            "project_id": self.project.id,
            "schema_version": self.schema_version,
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "components": len(self.components),
            "datasets": len(self.datasets),
            "metrics": len(self.metrics),
            "candidates": len(self.architecture_space.candidates),
        }

