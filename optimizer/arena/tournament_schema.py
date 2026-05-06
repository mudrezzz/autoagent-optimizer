"""Typed-схема конфигурации турнира Architecture Arena v0."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

# Имена метрик, которые могут использоваться в ranking policy.
ArenaRankingMetricName = Literal[
    "pass_rate",
    "passed",
    "failed",
    "participant_id",
    "coverage",
    "rule_violations_total",
    "nodes_executed_total",
    "avg_nodes_per_case",
    "llm_calls_total",
    "duration_ms_total",
    "duration_ms_avg",
    "p95_case_duration_ms",
    "composite_score",
]

# Числовые метрики для scoring (без строковых и производных composite полей).
ArenaScoringMetricName = Literal[
    "pass_rate",
    "passed",
    "failed",
    "coverage",
    "rule_violations_total",
    "nodes_executed_total",
    "avg_nodes_per_case",
    "llm_calls_total",
    "duration_ms_total",
    "duration_ms_avg",
    "p95_case_duration_ms",
]


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

    name: ArenaRankingMetricName = Field(
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


class ArenaScoringMetricSpec(BaseModel):
    """Конфиг одной метрики для composite scoring с направлением и весом."""

    name: ArenaScoringMetricName = Field(..., description="Имя числовой метрики для composite scoring.")
    direction: Literal["desc", "asc"] = Field(..., description="Направление оптимизации метрики.")
    weight: float = Field(..., gt=0.0, description="Нормированный вес метрики в composite scoring.")


class ArenaScoringPolicySpec(BaseModel):
    """Конфиг composite scoring policy для агрегирования middle-метрик в общий score."""

    enabled: bool = Field(default=False, description="Включает расчет `composite_score` для участников.")
    normalization: Literal["minmax"] = Field(
        default="minmax",
        description="Стратегия нормализации метрик перед взвешиванием.",
    )
    metrics: list[ArenaScoringMetricSpec] = Field(
        default_factory=lambda: [
            ArenaScoringMetricSpec(name="pass_rate", direction="desc", weight=0.7),
            ArenaScoringMetricSpec(name="failed", direction="asc", weight=0.2),
            ArenaScoringMetricSpec(name="rule_violations_total", direction="asc", weight=0.1),
        ],
        min_length=1,
        description="Набор метрик и весов для расчета composite score.",
    )

    @model_validator(mode="after")
    def validate_unique_metric_names(self) -> "ArenaScoringPolicySpec":
        """Проверяет, что каждая scoring-метрика задана только один раз."""

        names = [metric.name for metric in self.metrics]
        if len(set(names)) != len(names):
            raise ValueError("В scoring policy одна и та же метрика не должна дублироваться.")
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
    scoring: ArenaScoringPolicySpec = Field(default_factory=ArenaScoringPolicySpec, description="Scoring policy турнира.")
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

    @model_validator(mode="after")
    def validate_policy_consistency(self) -> "ArenaTournamentSpec":
        """Проверяет согласованность ranking/scoring политик в едином турнирном контракте."""

        ranking_metric_names = {metric.name for metric in self.ranking.metrics}
        if "composite_score" in ranking_metric_names and not self.scoring.enabled:
            raise ValueError("Метрика `composite_score` в ranking policy требует `scoring.enabled=true`.")
        return self
