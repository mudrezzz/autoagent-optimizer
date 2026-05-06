"""Модели node-level событий исполнения workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeEventStatus(str, Enum):
    """Поддерживаемые статусы событий выполнения узла."""

    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class NodeExecutionEvent(BaseModel):
    """Структурированное событие исполнения одного узла."""

    run_id: str = Field(..., min_length=1, description="Идентификатор runtime-прогона.")
    task_id: str = Field(..., min_length=1, description="Идентификатор бизнес-задачи/треда.")
    node_id: str = Field(..., min_length=1, description="Идентификатор узла Graph IR.")
    status: NodeEventStatus = Field(..., description="Статус события.")
    timestamp_utc: str = Field(..., min_length=1, description="UTC-время события в ISO8601 формате.")
    error: str | None = Field(default=None, description="Текст ошибки, если событие связано с failure.")
    details: dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные события.")

    def to_payload(self) -> dict[str, Any]:
        """Преобразует событие к JSON-совместимому словарю для state/CLI."""

        return self.model_dump(mode="json")


def utc_now_iso() -> str:
    """Возвращает текущее UTC-время в ISO8601 формате с timezone."""

    return datetime.now(timezone.utc).isoformat()

