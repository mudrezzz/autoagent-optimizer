"""Модель состояния исполнения рендеренного Graph IR workflow."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RenderedGraphState(BaseModel):
    """Единое состояние исполнения workflow, совместимое с BaseWorkflow."""

    payload: dict[str, Any] = Field(default_factory=dict, description="Пользовательский вход и промежуточные данные.")
    task_context: dict[str, Any] = Field(default_factory=dict, description="Служебный контекст задачи (task_id, run_id и др.).")
    active_nodes: list[str] = Field(default_factory=list, description="Текущие активные узлы для исполнения.")
    executed_nodes: list[str] = Field(default_factory=list, description="Узлы, которые уже были выполнены.")
    skipped_nodes: list[str] = Field(default_factory=list, description="Узлы, пропущенные из-за branch-условий.")
    node_outputs: dict[str, Any] = Field(default_factory=dict, description="Результаты выполнения узлов по их id.")
    trace: list[dict[str, Any]] = Field(default_factory=list, description="Упрощенный trace выполнения узлов.")
    node_events: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Node-level события `started/completed/failed/skipped` с run/task контекстом.",
    )
    trace_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Агрегированная сводка по trace для текущего run.",
    )
    errors: list[str] = Field(default_factory=list, description="Ошибки, пойманные в узлах при fallback-режиме.")

