"""Integration-тесты CLI экспорта Champion Bundle v0."""

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
def test_champion_export_bundle_cli_builds_artifacts_from_arena_file(tmp_path: Path) -> None:
    """Проверяет генерацию champion bundle по Arena YAML конфигу."""

    arena_file = _project_root() / "examples" / "arena" / "support_tournament_ci_decision_v0.yaml"
    out_dir = tmp_path / "champion_bundle"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "optimizer.champion.export_bundle",
            "--arena-file",
            str(arena_file),
            "--out-dir",
            str(out_dir),
            "--bundle-name",
            "stylizer_bundle_test",
            "--force",
            "--pretty",
        ],
        capture_output=True,
        text=True,
        cwd=_project_root(),
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "success"

    bundle_dir = Path(payload["bundle_dir"])
    manifest_file = Path(payload["manifest_file"])
    diagnostic_map_file = Path(payload["diagnostic_map_file"])
    evidence_json_file = Path(payload["evidence_pack_json_file"])
    generated_entrypoint_file = Path(payload["generated_agent_entrypoint_file"])
    parity_report_file = Path(payload["parity_report_file"])
    bundle_readme_file = Path(payload["bundle_readme_file"])

    assert bundle_dir.exists()
    assert manifest_file.exists()
    assert diagnostic_map_file.exists()
    assert evidence_json_file.exists()
    assert generated_entrypoint_file.exists()
    assert parity_report_file.exists()
    assert bundle_readme_file.exists()

    diagnostic_map_payload = json.loads(diagnostic_map_file.read_text(encoding="utf-8"))
    assert diagnostic_map_payload["version"] == "diagnostic_map_v0"
    assert "top_optimization_points" in diagnostic_map_payload

    manifest_payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_payload["version"] == "champion_bundle_v0"
    assert Path(manifest_payload["winner_graph_ir_file"]).exists()
    assert Path(manifest_payload["generated_agent_entrypoint_file"]).exists()
    assert Path(manifest_payload["parity_report_file"]).exists()
    assert Path(manifest_payload["bundle_readme_file"]).exists()

    parity_payload = json.loads(parity_report_file.read_text(encoding="utf-8"))
    assert parity_payload["version"] == "parity_report_v0"
    assert parity_payload["graph_ir_equivalent"] is True
    assert parity_payload["runtime_structural_parity"]["passed"] is True
