"""Unit-тесты preflight-проверки совместимости profile с native runtime target."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.evaluation.native_compatibility import build_native_compatibility_preflight_report
from optimizer.evaluation.profile_schema import EvaluationProfileSpec


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_native_compatibility_preflight_detects_supported_profile() -> None:
    """Проверяет, что профиль с direct_llm участниками совместим с native runtime v0."""

    dsl_file = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    payload = {
        "version": "evaluation_profile_v0",
        "profile_id": "native-compat-ok",
        "task_type": "native_runtime_smoke",
        "supported_targets": ["native_runtime"],
        "default_target": "native_runtime",
        "dataset_file": str(_project_root() / "examples" / "datasets" / "golden_support_v1.jsonl"),
        "evaluators": [{"evaluator_type": "golden_oracle"}],
        "comparative_metrics": [{"metric_id": "pass_rate", "direction": "desc", "weight": 1.0, "source": "oracle"}],
        "diagnostic_signals": [{"signal_id": "diag", "stage_scope": "synthesize", "aggregation": "avg"}],
        "participants": [
            {"participant_id": "a", "dsl_file": str(dsl_file), "stub_behavior": "perfect"},
            {"participant_id": "b", "dsl_file": str(dsl_file), "stub_behavior": "fail_all"},
        ],
    }
    profile = EvaluationProfileSpec.model_validate(payload)

    report = build_native_compatibility_preflight_report(profile=profile, profile_file_dir=_project_root())
    assert report.can_execute_native is True
    assert report.incompatible_total == 0
    assert all(item.compatible for item in report.participants)


@pytest.mark.unit
def test_native_compatibility_preflight_detects_unsupported_hitl_node() -> None:
    """Проверяет, что preflight ловит `hitl_gate` как unsupported node kind для native v0."""

    dsl_ok = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    dsl_hitl = _project_root() / "examples" / "dsl" / "style_hitl_reviewer.yaml"
    payload = {
        "version": "evaluation_profile_v0",
        "profile_id": "native-compat-bad",
        "task_type": "style_rewrite_social_post",
        "supported_targets": ["native_runtime"],
        "default_target": "native_runtime",
        "dataset_file": str(_project_root() / "examples" / "datasets" / "golden_linkedin_stylizer_v1.jsonl"),
        "evaluators": [{"evaluator_type": "golden_oracle"}],
        "comparative_metrics": [{"metric_id": "pass_rate", "direction": "desc", "weight": 1.0, "source": "oracle"}],
        "diagnostic_signals": [{"signal_id": "diag", "stage_scope": "validate", "aggregation": "sum"}],
        "participants": [
            {"participant_id": "ok", "dsl_file": str(dsl_ok), "stub_behavior": "perfect"},
            {"participant_id": "hitl", "dsl_file": str(dsl_hitl), "stub_behavior": "fail_all"},
        ],
    }
    profile = EvaluationProfileSpec.model_validate(payload)

    report = build_native_compatibility_preflight_report(profile=profile, profile_file_dir=_project_root())
    assert report.can_execute_native is False
    assert report.incompatible_total == 1

    hitl_participant = next(item for item in report.participants if item.participant_id == "hitl")
    assert hitl_participant.compatible is False
    assert any(issue.kind == "hitl_gate" for issue in hitl_participant.issues)
