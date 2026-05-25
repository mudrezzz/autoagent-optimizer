"""Unit-тесты compile-readiness gate для C2 candidate set."""

from __future__ import annotations

from pathlib import Path

from optimizer.c2 import build_candidate_draft_from_brief, run_compile_readiness_gate_for_candidate_set


def test_compile_gate_marks_candidates_ready_for_valid_dsl() -> None:
    """Проверяет, что compile gate отмечает валидные DSL-кандидаты как ready."""

    project_root = Path(__file__).resolve().parents[2]
    draft = build_candidate_draft_from_brief(
        arena_id="arena_demo_1",
        brief="Собери кандидатов для стилизатора постов.",
        max_candidates=2,
    )

    compiled = run_compile_readiness_gate_for_candidate_set(candidate_set_draft=draft, project_root=project_root)

    assert compiled["compile_gate"]["status"] == "ready"
    assert compiled["compile_gate"]["ready_candidates"] == 2
    assert compiled["compile_gate"]["failed_candidates"] == 0
    for candidate in compiled["candidates"]:
        readiness = candidate["compile_readiness"]
        assert readiness["status"] == "ready"
        assert readiness["compile_summary"]["status"] == "success"
        assert readiness["graph_ir_summary"]["available"] is True


def test_compile_gate_marks_failed_when_candidate_dsl_is_missing() -> None:
    """Проверяет failed-ветку compile gate при отсутствующем DSL-файле кандидата."""

    project_root = Path(__file__).resolve().parents[2]
    draft = build_candidate_draft_from_brief(
        arena_id="arena_demo_1",
        brief="Собери кандидатов для стилизатора постов.",
        max_candidates=1,
    )
    draft["candidates"][0]["dsl_stub_ref"] = "examples/dsl/missing_file.yaml"

    compiled = run_compile_readiness_gate_for_candidate_set(candidate_set_draft=draft, project_root=project_root)

    assert compiled["compile_gate"]["status"] == "failed"
    assert compiled["compile_gate"]["ready_candidates"] == 0
    assert compiled["compile_gate"]["failed_candidates"] == 1
    readiness = compiled["candidates"][0]["compile_readiness"]
    assert readiness["status"] == "failed"
    assert readiness["compile_summary"]["errors"] == 1
    assert readiness["issues"][0]["severity"] == "error"
