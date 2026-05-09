"""Unit-тесты схемы Evaluation Profile v0."""

from __future__ import annotations

import pytest

from optimizer.evaluation.profile_schema import EvaluationProfileSpec


@pytest.mark.unit
def test_evaluation_profile_schema_accepts_valid_profile() -> None:
    """Проверяет успешную валидацию корректного evaluation profile."""

    payload = {
        "version": "evaluation_profile_v0",
        "profile_id": "profile-ok",
        "task_type": "style_rewrite_social_post",
        "supported_targets": ["dsl_runtime", "native_runtime"],
        "default_target": "dsl_runtime",
        "dataset_file": "./dataset.jsonl",
        "dsl_execution_mode": "expected_stub",
        "task_prefix": "profile-task",
        "budget": {"cases_limit": 4, "selector": "head", "random_seed": 42},
        "evaluators": [{"evaluator_type": "golden_oracle", "config": {}, "budget": {}}],
        "comparative_metrics": [
            {"metric_id": "pass_rate", "direction": "desc", "weight": 0.7, "source": "golden_oracle"},
            {"metric_id": "duration_ms_avg", "direction": "asc", "weight": 0.3, "source": "runtime_trace"},
        ],
        "diagnostic_signals": [
            {"signal_id": "diag-1", "stage_scope": "synthesize", "aggregation": "avg"},
            {"signal_id": "diag-2", "stage_scope": "validate", "aggregation": "sum"},
        ],
        "participants": [
            {"participant_id": "p1", "dsl_file": "a.yaml", "stub_behavior": "perfect"},
            {"participant_id": "p2", "dsl_file": "b.yaml", "stub_behavior": "fail_all"},
        ],
    }

    spec = EvaluationProfileSpec.model_validate(payload)
    assert spec.profile_id == "profile-ok"
    assert spec.default_target == "dsl_runtime"
    assert "native_runtime" in spec.supported_targets


@pytest.mark.unit
def test_evaluation_profile_schema_rejects_unknown_default_target() -> None:
    """Проверяет ошибку, если default target не входит в список supported targets."""

    payload = {
        "version": "evaluation_profile_v0",
        "profile_id": "profile-bad-target",
        "task_type": "style_rewrite_social_post",
        "supported_targets": ["dsl_runtime"],
        "default_target": "native_runtime",
        "dataset_file": "./dataset.jsonl",
        "comparative_metrics": [{"metric_id": "pass_rate", "direction": "desc", "weight": 1.0, "source": "oracle"}],
        "diagnostic_signals": [{"signal_id": "diag-1", "stage_scope": "synthesize", "aggregation": "avg"}],
        "participants": [
            {"participant_id": "p1", "dsl_file": "a.yaml", "stub_behavior": "perfect"},
            {"participant_id": "p2", "dsl_file": "b.yaml", "stub_behavior": "fail_all"},
        ],
    }

    with pytest.raises(ValueError):
        EvaluationProfileSpec.model_validate(payload)


@pytest.mark.unit
def test_evaluation_profile_schema_rejects_duplicate_comparative_metrics() -> None:
    """Проверяет ошибку при дублировании `metric_id` в comparative metrics."""

    payload = {
        "version": "evaluation_profile_v0",
        "profile_id": "profile-bad-metric",
        "task_type": "style_rewrite_social_post",
        "supported_targets": ["dsl_runtime"],
        "default_target": "dsl_runtime",
        "dataset_file": "./dataset.jsonl",
        "comparative_metrics": [
            {"metric_id": "pass_rate", "direction": "desc", "weight": 0.7, "source": "oracle"},
            {"metric_id": "pass_rate", "direction": "asc", "weight": 0.3, "source": "oracle"},
        ],
        "diagnostic_signals": [{"signal_id": "diag-1", "stage_scope": "synthesize", "aggregation": "avg"}],
        "participants": [
            {"participant_id": "p1", "dsl_file": "a.yaml", "stub_behavior": "perfect"},
            {"participant_id": "p2", "dsl_file": "b.yaml", "stub_behavior": "fail_all"},
        ],
    }

    with pytest.raises(ValueError):
        EvaluationProfileSpec.model_validate(payload)
