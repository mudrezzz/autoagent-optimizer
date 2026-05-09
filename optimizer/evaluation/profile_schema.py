"""Typed-схема profile-driven оценки задач (Evaluation Profile v0)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from optimizer.arena.tournament_schema import ArenaParticipantSpec

# Доступные runtime-таргеты исполнения evaluation profile.
EvaluationExecutionTarget = Literal["dsl_runtime", "native_runtime"]

# Типы evaluator-этапов для profile-driven chain v0.
EvaluationEvaluatorType = Literal["golden_oracle"]

# Stage taxonomy для диагностических сигналов v0.
EvaluationStageScope = Literal[
    "retrieve",
    "rerank",
    "synthesize",
    "validate",
    "tool_call",
    "hitl",
    "transform",
    "unknown",
]

# Метрики, поддерживаемые в comparative-слое и scoring/ranking пути.
EvaluationComparativeMetricName = Literal[
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


class EvaluationProfileBudgetSpec(BaseModel):
    """Бюджетные ограничения profile-run v0."""

    cases_limit: int = Field(default=0, ge=0, description="Лимит кейсов (0 = весь dataset).")
    selector: Literal["head", "random_seeded", "hash_stable"] = Field(
        default="head",
        description="Стратегия выбора кейсов при ограниченном бюджете.",
    )
    random_seed: int = Field(default=42, ge=0, description="Сид для `random_seeded`/`hash_stable`.")
    max_llm_calls: int = Field(default=0, ge=0, description="Лимит LLM-вызовов (0 = без лимита в v0).")
    max_input_tokens: int = Field(default=0, ge=0, description="Лимит входных токенов (0 = без лимита в v0).")
    max_output_tokens: int = Field(default=0, ge=0, description="Лимит выходных токенов (0 = без лимита в v0).")
    max_usd: float = Field(default=0.0, ge=0.0, description="Лимит стоимости в USD (0 = без лимита в v0).")
    max_wall_time_sec: int = Field(default=0, ge=0, description="Лимит wall-time в секундах (0 = без лимита в v0).")


class EvaluationComparativeMetricSpec(BaseModel):
    """Конфиг одной comparative-метрики для ranking/scoring слоя."""

    metric_id: EvaluationComparativeMetricName = Field(..., description="Идентификатор comparative-метрики.")
    direction: Literal["desc", "asc"] = Field(..., description="Направление оптимизации метрики.")
    weight: float = Field(default=1.0, gt=0.0, description="Вес метрики в composite scoring.")
    source: str = Field(
        default="golden_oracle",
        min_length=1,
        description="Источник метрики (oracle/runtime_trace/adapter id).",
    )


class EvaluationDiagnosticSignalSpec(BaseModel):
    """Конфиг одного диагностического сигнала по stage-scope."""

    signal_id: str = Field(..., min_length=1, description="Идентификатор диагностического сигнала.")
    stage_scope: EvaluationStageScope = Field(..., description="Стадия пайплайна, на которую направлен сигнал.")
    aggregation: Literal["sum", "avg", "p95", "count"] = Field(
        default="avg",
        description="Способ агрегирования сигнала в отчете.",
    )


class EvaluationEvaluatorSpec(BaseModel):
    """Конфиг одного evaluator-этапа в profile-chain."""

    evaluator_type: EvaluationEvaluatorType = Field(..., description="Тип evaluator-а.")
    config: dict[str, object] = Field(default_factory=dict, description="Свободный config evaluator-а.")
    budget: dict[str, object] = Field(default_factory=dict, description="Локальный budget evaluator-а.")


class EvaluationProfileSpec(BaseModel):
    """Единый контракт profile-driven оценки задачи."""

    version: Literal["evaluation_profile_v0"] = Field(
        default="evaluation_profile_v0",
        description="Версия контракта profile-driven оценки.",
    )
    profile_id: str = Field(..., min_length=1, description="Уникальный идентификатор evaluation profile.")
    task_type: str = Field(..., min_length=1, description="Тип задачи/домена, под который настроен профиль.")
    supported_targets: list[EvaluationExecutionTarget] = Field(
        default_factory=lambda: ["dsl_runtime"],
        min_length=1,
        description="Набор runtime-таргетов, поддерживаемых профилем.",
    )
    default_target: EvaluationExecutionTarget = Field(
        default="dsl_runtime",
        description="Таргет по умолчанию для CLI-запуска профиля.",
    )
    dataset_file: str = Field(..., min_length=1, description="Путь до golden dataset JSONL.")
    dsl_execution_mode: Literal["expected_stub", "runtime"] = Field(
        default="expected_stub",
        description="Режим dsl-runtime исполнения для `dsl_runtime` target.",
    )
    task_prefix: str = Field(default="profile-task", min_length=1, description="Префикс task_id для runtime запуска.")
    budget: EvaluationProfileBudgetSpec = Field(
        default_factory=EvaluationProfileBudgetSpec,
        description="Budget policy профиля.",
    )
    evaluators: list[EvaluationEvaluatorSpec] = Field(
        default_factory=lambda: [EvaluationEvaluatorSpec(evaluator_type="golden_oracle")],
        min_length=1,
        description="Evaluator chain профиля.",
    )
    comparative_metrics: list[EvaluationComparativeMetricSpec] = Field(
        ...,
        min_length=1,
        description="Сравнительные метрики для ranking/scoring.",
    )
    diagnostic_signals: list[EvaluationDiagnosticSignalSpec] = Field(
        ...,
        min_length=1,
        description="Диагностические сигналы для root-cause анализа.",
    )
    participants: list[ArenaParticipantSpec] = Field(..., min_length=2, max_length=3, description="Кандидаты сравнения.")

    @model_validator(mode="after")
    def validate_profile_consistency(self) -> "EvaluationProfileSpec":
        """Проверяет консистентность таргетов и уникальность metric/signal идентификаторов."""

        if self.default_target not in self.supported_targets:
            raise ValueError("`default_target` должен входить в `supported_targets`.")

        metric_ids = [metric.metric_id for metric in self.comparative_metrics]
        if len(set(metric_ids)) != len(metric_ids):
            raise ValueError("В `comparative_metrics` нельзя дублировать `metric_id`.")

        signal_ids = [signal.signal_id for signal in self.diagnostic_signals]
        if len(set(signal_ids)) != len(signal_ids):
            raise ValueError("В `diagnostic_signals` нельзя дублировать `signal_id`.")

        return self
