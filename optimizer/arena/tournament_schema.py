"""Typed-схема конфигурации турнира Architecture Arena v0."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ArenaParticipantSpec(BaseModel):
    """Описание одного кандидата архитектуры в турнире."""

    participant_id: str = Field(..., min_length=1, description="Уникальный идентификатор участника.")
    dsl_file: str = Field(default="", description="Путь до DSL YAML спецификации участника.")
    graph_ir_file: str = Field(default="", description="Путь до Graph IR JSON спецификации участника.")
    stub_behavior: Literal["perfect", "fail_all", "fail_sensitive"] = Field(
        default="perfect",
        description="Детерминированный профиль поведения в expected_stub режиме.",
    )

    @model_validator(mode="after")
    def validate_single_source(self) -> "ArenaParticipantSpec":
        """Проверяет, что у участника задан ровно один источник: DSL или Graph IR."""

        has_dsl = bool(self.dsl_file.strip())
        has_ir = bool(self.graph_ir_file.strip())
        if has_dsl == has_ir:
            raise ValueError("Участник должен задать ровно один источник: `dsl_file` или `graph_ir_file`.")
        return self


class ArenaTournamentSpec(BaseModel):
    """Конфигурация турнира Arena v0 с общим бюджетом для всех участников."""

    version: Literal["arena_v0"] = Field(default="arena_v0", description="Версия контракта конфигурации.")
    dataset_file: str = Field(..., min_length=1, description="Путь до golden dataset JSONL.")
    execution_mode: Literal["expected_stub", "runtime"] = Field(
        default="expected_stub",
        description="Режим исполнения участников: deterministic stub или runtime workflow.",
    )
    budget_policy: Literal["equal_cases"] = Field(
        default="equal_cases",
        description="Политика распределения бюджета между участниками.",
    )
    cases_limit: int = Field(default=0, ge=0, description="Ограничение числа кейсов на участника (0 = все).")
    task_prefix: str = Field(default="arena-task", min_length=1, description="Префикс task_id для runtime режима.")
    participants: list[ArenaParticipantSpec] = Field(..., min_length=2, max_length=3, description="Кандидаты турнира.")

