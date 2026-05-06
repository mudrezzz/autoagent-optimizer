"""Модели отчета компиляции DSL -> Graph IR."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CompileStatus(str, Enum):
    """Статус результата компиляции."""

    SUCCESS = "success"
    FAILURE = "failure"


class CompileIssueSeverity(str, Enum):
    """Уровень серьезности сообщения компилятора."""

    WARNING = "warning"
    ERROR = "error"


class CompileIssue(BaseModel):
    """Сообщение компилятора с указанием уровня и контекста."""

    severity: CompileIssueSeverity = Field(..., description="Критичность сообщения.")
    message: str = Field(..., min_length=1, description="Текст сообщения.")
    context: dict[str, Any] = Field(default_factory=dict, description="Контекст сообщения для диагностики.")


class NodeMappingRecord(BaseModel):
    """Соответствие узла DSL и узла Graph IR."""

    dsl_node_id: str = Field(..., min_length=1, description="Идентификатор узла в DSL.")
    ir_node_id: str = Field(..., min_length=1, description="Идентификатор узла в Graph IR.")
    dsl_type: str = Field(..., min_length=1, description="Тип узла в DSL.")
    ir_kind: str = Field(..., min_length=1, description="Тип узла в Graph IR.")
    component_id: str = Field(..., min_length=1, description="Идентификатор компонента в DSL.")
    component_ref: str = Field(..., min_length=1, description="Референс компонента в IR.")


class DslCompileReport(BaseModel):
    """Итоговый отчет компиляции DSL в Graph IR."""

    status: CompileStatus = Field(..., description="Финальный статус компиляции.")
    source: str = Field(..., min_length=1, description="Источник DSL (обычно путь к файлу).")
    node_mappings: list[NodeMappingRecord] = Field(
        default_factory=list,
        description="Таблица соответствия узлов DSL и IR.",
    )
    issues: list[CompileIssue] = Field(default_factory=list, description="Список предупреждений и ошибок компиляции.")

    def add_warning(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        """Добавляет предупреждение в отчет компиляции."""

        self.issues.append(
            CompileIssue(
                severity=CompileIssueSeverity.WARNING,
                message=message,
                context=dict(context or {}),
            )
        )

    def add_error(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        """Добавляет ошибку в отчет компиляции."""

        self.issues.append(
            CompileIssue(
                severity=CompileIssueSeverity.ERROR,
                message=message,
                context=dict(context or {}),
            )
        )

    def summary(self) -> dict[str, int | str]:
        """Возвращает агрегированную сводку отчета."""

        warning_count = sum(1 for issue in self.issues if issue.severity == CompileIssueSeverity.WARNING)
        error_count = sum(1 for issue in self.issues if issue.severity == CompileIssueSeverity.ERROR)
        return {
            "status": self.status.value,
            "source": self.source,
            "node_mappings": len(self.node_mappings),
            "warnings": warning_count,
            "errors": error_count,
        }

