"""Integration-тесты CLI parity harness (`optimizer.parity.run`)."""

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
def test_parity_cli_runs_on_stylizer_profile() -> None:
    """Проверяет успешный parity-run на canonical stylizer profile."""

    profile_file = _project_root() / "examples" / "profiles" / "stylizer_profile_ci_v0.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.parity.run",
            "--profile-file",
            str(profile_file),
            "--cases-limit",
            "1",
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["version"] == "dsl_native_parity_v0"
    assert payload["profile_id"] == "stylizer_profile_ci_v0"
    assert payload["participants_total"] == 3
    assert payload["participants_failed"] == 0
    assert payload["passed"] is True


@pytest.mark.integration
def test_parity_cli_fail_on_mismatch_gate_on_invalid_participant_filter() -> None:
    """Проверяет fail-fast поведение parity CLI при некорректном participant фильтре."""

    profile_file = _project_root() / "examples" / "profiles" / "stylizer_profile_ci_v0.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.parity.run",
            "--profile-file",
            str(profile_file),
            "--cases-limit",
            "1",
            "--participant-id",
            "unknown_participant",
            "--fail-on-mismatch",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 1
    assert "[PARITY ERROR]" in proc.stderr
