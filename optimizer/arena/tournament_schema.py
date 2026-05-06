"""Typed-схема конфигурации турнира Architecture Arena v0."""

from __future__ import annotations

from typing import Any, Literal

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


class ArenaBudgetPolicySpec(BaseModel):
    """Конфиг бюджетной политики турнира."""

    policy: Literal["equal_cases"] = Field(default="equal_cases", description="Текущая политика распределения бюджета.")
    unit: Literal["cases"] = Field(default="cases", description="Единица измерения бюджета.")
    selector: Literal["head", "random_seeded", "hash_stable"] = Field(
        default="head",
        description="Способ выбора подмножества кейсов при ограниченном бюджете.",
    )
    limit: int = Field(default=0, ge=0, description="Лимит кейсов на участника (0 = все кейсы).")
    random_seed: int = Field(default=42, ge=0, description="Сид для `random_seeded`/`hash_stable` selectors.")


class ArenaRankingMetricSpec(BaseModel):
    """Описание одной метрики ранжирования и направления сортировки."""

    name: Literal["pass_rate", "passed", "failed", "participant_id"] = Field(
        ...,
        description="Имя метрики ранжирования участников.",
    )
    direction: Literal["desc", "asc"] = Field(..., description="Направление сортировки метрики.")


class ArenaRankingPolicySpec(BaseModel):
    """Конфиг ranking policy с первичной метрикой и tie-break метриками."""

    metrics: list[ArenaRankingMetricSpec] = Field(
        default_factory=lambda: [
            ArenaRankingMetricSpec(name="pass_rate", direction="desc"),
            ArenaRankingMetricSpec(name="passed", direction="desc"),
            ArenaRankingMetricSpec(name="failed", direction="asc"),
            ArenaRankingMetricSpec(name="participant_id", direction="asc"),
        ],
        min_length=1,
        description="Упорядоченный список ranking метрик с направлением.",
    )

    @model_validator(mode="after")
    def validate_unique_metric_names(self) -> "ArenaRankingPolicySpec":
        """Проверяет, что каждая метрика в ranking policy используется один раз."""

        names = [metric.name for metric in self.metrics]
        if len(set(names)) != len(names):
            raise ValueError("В ranking policy одна и та же метрика не должна дублироваться.")
        return self


class ArenaEvaluatorPolicySpec(BaseModel):
    """Конфиг evaluator policy для сравнения участников."""

    mode: Literal["rule_based_v0"] = Field(
        default="rule_based_v0",
        description="Режим оценки результатов участников (текущая реализация rule-based).",
    )


class ArenaTournamentSpec(BaseModel):
    """Конфигурация турнира Arena v0 с config-first политиками сравнения."""

    version: Literal["arena_v0"] = Field(default="arena_v0", description="Версия контракта конфигурации.")
    dataset_file: str = Field(..., min_length=1, description="Путь до golden dataset JSONL.")
    execution_mode: Literal["expected_stub", "runtime"] = Field(
        default="expected_stub",
        description="Режим исполнения участников: deterministic stub или runtime workflow.",
    )
    task_prefix: str = Field(default="arena-task", min_length=1, description="Префикс task_id для runtime режима.")
    budget: ArenaBudgetPolicySpec = Field(default_factory=ArenaBudgetPolicySpec, description="Бюджетная политика турнира.")
    ranking: ArenaRankingPolicySpec = Field(default_factory=ArenaRankingPolicySpec, description="Ranking policy турнира.")
    evaluator: ArenaEvaluatorPolicySpec = Field(
        default_factory=ArenaEvaluatorPolicySpec,
        description="Evaluator policy для оценки участников.",
    )
    participants: list[ArenaParticipantSpec] = Field(..., min_length=2, max_length=3, description="Кандидаты турнира.")

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_budget_fields(cls, data: Any) -> Any:
        """Поддерживает legacy-поля `budget_policy`/`cases_limit` через миграцию в `budget`."""

        if not isinstance(data, dict):
            return data
        if "budget" in data:
            return data

        budget_policy = data.get("budget_policy", "equal_cases")
        cases_limit = data.get("cases_limit", 0)
        data["budget"] = {
            "policy": budget_policy,
            "unit": "cases",
            "selector": "head",
            "limit": cases_limit,
            "random_seed": 42,
        }
        return data
