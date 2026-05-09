"""Integration-тесты CLI запуска Evaluation Profile v0."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_evaluation_profile_cli_runs_dsl_target_from_examples() -> None:
    """Проверяет успешный CLI-запуск example profile на `dsl_runtime` target."""

    profile_file = _project_root() / "examples" / "profiles" / "stylizer_profile_ci_v0.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evaluation.run_profile",
            "--profile-file",
            str(profile_file),
            "--target",
            "dsl_runtime",
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr

    payload = json.loads(proc.stdout)
    assert payload["profile_id"] == "stylizer_profile_ci_v0"
    assert payload["execution_target"] == "dsl_runtime"
    assert payload["result"]["winner_id"] == "style_direct_candidate"
    assert payload["result"]["cases_budget"] == 4
    assert "comparison" in payload["result"]
    assert "diagnostics" in payload["result"]


@pytest.mark.integration
def test_evaluation_profile_cli_runs_native_target_with_temp_profile(tmp_path: Path) -> None:
    """Проверяет запуск `native_runtime` target на минимальном временном профиле."""

    dataset_file = tmp_path / "dataset.jsonl"
    dataset_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "case_id": "case-1",
                        "input": {"query": "Сформируй короткий ответ"},
                        "expected": {"must_include": ["[mock-llm]"], "forbidden": []},
                        "tags": ["smoke"],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "case_id": "case-2",
                        "input": {"query": "Еще один короткий ответ"},
                        "expected": {"must_include": ["[mock-llm]"], "forbidden": []},
                        "tags": ["smoke"],
                    },
                    ensure_ascii=False,
                ),
            ]
        ),
        encoding="utf-8",
    )
    dsl_file = _project_root() / "examples" / "dsl" / "direct_llm.yaml"
    profile_file = tmp_path / "native_profile.yaml"
    profile_file.write_text(
        "\n".join(
            [
                "version: evaluation_profile_v0",
                "profile_id: native_profile_test_v0",
                "task_type: native_runtime_smoke",
                "supported_targets:",
                "  - dsl_runtime",
                "  - native_runtime",
                "default_target: native_runtime",
                f"dataset_file: {dataset_file.as_posix()}",
                "dsl_execution_mode: runtime",
                "task_prefix: native-profile-test",
                "budget:",
                "  cases_limit: 2",
                "  selector: head",
                "  random_seed: 42",
                "evaluators:",
                "  - evaluator_type: golden_oracle",
                "    config: {}",
                "    budget: {}",
                "comparative_metrics:",
                "  - metric_id: pass_rate",
                "    direction: desc",
                "    weight: 0.8",
                "    source: golden_oracle",
                "  - metric_id: duration_ms_avg",
                "    direction: asc",
                "    weight: 0.2",
                "    source: runtime_trace",
                "diagnostic_signals:",
                "  - signal_id: synth_diag",
                "    stage_scope: synthesize",
                "    aggregation: avg",
                "  - signal_id: validate_diag",
                "    stage_scope: validate",
                "    aggregation: sum",
                "participants:",
                "  - participant_id: native_candidate_a",
                f"    dsl_file: {dsl_file.as_posix()}",
                "    stub_behavior: perfect",
                "  - participant_id: native_candidate_b",
                f"    dsl_file: {dsl_file.as_posix()}",
                "    stub_behavior: fail_all",
            ]
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.evaluation.run_profile",
            "--profile-file",
            str(profile_file),
            "--target",
            "native_runtime",
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr

    payload = json.loads(proc.stdout)
    assert payload["profile_id"] == "native_profile_test_v0"
    assert payload["execution_target"] == "native_runtime"
    assert payload["result"]["execution_mode"] == "native_runtime"
    assert payload["result"]["cases_budget"] == 2
    assert len(payload["result"]["participants"]) == 2
    assert payload["result"]["winner_id"] in {"native_candidate_a", "native_candidate_b"}
