"""Unit-тесты турнирного ранжирования и equal-budget логики Arena runner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from optimizer.arena.runner import ArchitectureArenaRunner
from optimizer.arena.tournament_schema import ArenaParticipantSpec, ArenaTournamentSpec


def _write_dataset(path: Path) -> None:
    """Создает минимальный golden dataset для unit-проверки ранжирования."""

    rows = [
        {
            "case_id": "c1",
            "input": {"query": "q1"},
            "expected": {"must_include": ["alpha"], "forbidden": []},
            "tags": ["support"],
        },
        {
            "case_id": "c2",
            "input": {"query": "q2"},
            "expected": {"must_include": ["beta"], "forbidden": []},
            "tags": ["support"],
        },
        {
            "case_id": "c3",
            "input": {"query": "q3"},
            "expected": {"must_include": ["gamma"], "forbidden": ["blocked"]},
            "tags": ["sensitive"],
        },
    ]
    payload = "\n".join(json.dumps(item, ensure_ascii=False) for item in rows)
    path.write_text(payload, encoding="utf-8")


@pytest.mark.unit
def test_arena_runner_ranks_participants_by_pass_rate(tmp_path: Path) -> None:
    """Проверяет, что runner ранжирует участников по pass_rate и выбирает чемпиона."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)
    spec = ArenaTournamentSpec(
        dataset_file=dataset_file.name,
        execution_mode="expected_stub",
        participants=[
            ArenaParticipantSpec(participant_id="champion", dsl_file="a.yaml", stub_behavior="perfect"),
            ArenaParticipantSpec(participant_id="middle", dsl_file="b.yaml", stub_behavior="fail_sensitive"),
            ArenaParticipantSpec(participant_id="weak", dsl_file="c.yaml", stub_behavior="fail_all"),
        ],
    )

    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)

    assert result.winner_id == "champion"
    assert result.ranking == ["champion", "middle", "weak"]
    assert result.participants[0].pass_rate == 1.0
    assert result.participants[0].passed == 3
    assert result.participants[1].passed == 2
    assert result.participants[2].passed == 0


@pytest.mark.unit
def test_arena_runner_applies_equal_case_budget_limit(tmp_path: Path) -> None:
    """Проверяет, что `cases_limit` одинаково ограничивает бюджет кейсов для всех участников."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)
    spec = ArenaTournamentSpec(
        dataset_file=dataset_file.name,
        execution_mode="expected_stub",
        cases_limit=2,
        participants=[
            ArenaParticipantSpec(participant_id="p1", dsl_file="a.yaml", stub_behavior="perfect"),
            ArenaParticipantSpec(participant_id="p2", dsl_file="b.yaml", stub_behavior="perfect"),
        ],
    )

    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)

    assert result.cases_budget == 2
    assert result.evaluated_records_total == 2
    assert all(participant.cases_total == 2 for participant in result.participants)


@pytest.mark.unit
def test_arena_runner_uses_config_driven_ranking_policy(tmp_path: Path) -> None:
    """Проверяет, что winner определяется настройками ranking policy, а не фиксированным порядком."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)
    spec = ArenaTournamentSpec(
        dataset_file=dataset_file.name,
        execution_mode="expected_stub",
        ranking={
            "metrics": [
                {"name": "failed", "direction": "desc"},
                {"name": "participant_id", "direction": "asc"},
            ]
        },
        participants=[
            ArenaParticipantSpec(participant_id="a", dsl_file="a.yaml", stub_behavior="perfect"),
            ArenaParticipantSpec(participant_id="b", dsl_file="b.yaml", stub_behavior="fail_sensitive"),
            ArenaParticipantSpec(participant_id="c", dsl_file="c.yaml", stub_behavior="fail_all"),
        ],
    )

    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)

    assert result.ranking == ["c", "b", "a"]
    assert result.winner_id == "c"


@pytest.mark.unit
def test_arena_runner_applies_hash_stable_budget_selector_deterministically(tmp_path: Path) -> None:
    """Проверяет детерминированность выбора кейсов при `hash_stable` budget selector."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)
    spec = ArenaTournamentSpec(
        dataset_file=dataset_file.name,
        execution_mode="expected_stub",
        budget={
            "policy": "equal_cases",
            "unit": "cases",
            "selector": "hash_stable",
            "limit": 2,
            "random_seed": 7,
        },
        participants=[
            ArenaParticipantSpec(participant_id="p1", dsl_file="a.yaml", stub_behavior="perfect"),
            ArenaParticipantSpec(participant_id="p2", dsl_file="b.yaml", stub_behavior="perfect"),
        ],
    )

    runner = ArchitectureArenaRunner()
    result_1 = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)
    result_2 = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)

    assert result_1.cases_budget == 2
    assert result_1.evaluated_records_total == 2
    assert result_1.ranking == result_2.ranking
    assert result_1.participants[0].passed == result_2.participants[0].passed


@pytest.mark.unit
def test_arena_runner_calculates_middle_metrics_and_composite_score(tmp_path: Path) -> None:
    """Проверяет расчет middle-метрик и composite score по scoring policy."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)
    spec = ArenaTournamentSpec(
        dataset_file=dataset_file.name,
        execution_mode="expected_stub",
        ranking={
            "metrics": [
                {"name": "composite_score", "direction": "desc"},
                {"name": "participant_id", "direction": "asc"},
            ]
        },
        scoring={
            "enabled": True,
            "normalization": "minmax",
            "metrics": [
                {"name": "pass_rate", "direction": "desc", "weight": 0.8},
                {"name": "rule_violations_total", "direction": "asc", "weight": 0.2},
            ],
        },
        participants=[
            ArenaParticipantSpec(participant_id="champion", dsl_file="a.yaml", stub_behavior="perfect"),
            ArenaParticipantSpec(participant_id="weak", dsl_file="b.yaml", stub_behavior="fail_all"),
        ],
    )

    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)

    assert result.winner_id == "champion"
    champion = result.participants[0]
    weak = result.participants[1]
    assert champion.composite_score is not None
    assert weak.composite_score is not None
    assert champion.composite_score > weak.composite_score
    assert "coverage" in champion.middle_metrics
    assert "rule_violations_total" in champion.middle_metrics
    assert "duration_ms_avg" in champion.middle_metrics


@pytest.mark.unit
def test_arena_runner_rejects_composite_ranking_without_scoring(tmp_path: Path) -> None:
    """Проверяет, что `composite_score` в ranking policy требует включенного scoring."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)

    with pytest.raises(ValueError):
        ArenaTournamentSpec(
            dataset_file=dataset_file.name,
            execution_mode="expected_stub",
            ranking={
                "metrics": [
                    {"name": "composite_score", "direction": "desc"},
                    {"name": "participant_id", "direction": "asc"},
                ]
            },
            participants=[
                ArenaParticipantSpec(participant_id="a", dsl_file="a.yaml", stub_behavior="perfect"),
                ArenaParticipantSpec(participant_id="b", dsl_file="b.yaml", stub_behavior="perfect"),
            ],
        )


@pytest.mark.unit
def test_arena_runner_emits_dual_metrics_contract(tmp_path: Path) -> None:
    """Проверяет наличие секций `comparison` и `diagnostics` в итоговом JSON турнира."""

    dataset_file = tmp_path / "dataset.jsonl"
    _write_dataset(dataset_file)
    spec = ArenaTournamentSpec(
        dataset_file=dataset_file.name,
        execution_mode="expected_stub",
        participants=[
            ArenaParticipantSpec(participant_id="a", dsl_file="a.yaml", stub_behavior="perfect"),
            ArenaParticipantSpec(participant_id="b", dsl_file="b.yaml", stub_behavior="fail_all"),
        ],
    )

    runner = ArchitectureArenaRunner()
    result = runner.run(spec=spec, arena_file_dir=tmp_path, include_details=False)
    payload = result.to_payload()

    assert "comparison" in payload
    assert "diagnostics" in payload
    assert payload["comparison"]["winner_id"] == payload["winner_id"]
    assert len(payload["comparison"]["participants"]) == 2
    assert len(payload["diagnostics"]["participants"]) == 2
    assert "signals" in payload["diagnostics"]["participants"][0]
