"""Unit-тесты контракта расширенного stylizer dataset для демо-арены."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.evaluation.dataset_loader import GoldenDatasetLoader


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_stylizer_dataset_has_expected_minimum_volume() -> None:
    """Проверяет, что stylizer dataset расширен и содержит минимум 12 кейсов."""

    loader = GoldenDatasetLoader()
    dataset_file = _project_root() / "examples" / "datasets" / "golden_linkedin_stylizer_v1.jsonl"
    result = loader.load_file(dataset_file)
    assert result.is_success is True
    assert len(result.records) >= 12


@pytest.mark.unit
def test_stylizer_dataset_contains_multiline_long_posts() -> None:
    """Проверяет, что демо-кейсы содержат длинные многоабзацные посты, а не короткие строки."""

    loader = GoldenDatasetLoader()
    dataset_file = _project_root() / "examples" / "datasets" / "golden_linkedin_stylizer_v1.jsonl"
    result = loader.load_file(dataset_file)
    assert result.is_success is True

    multiline_cases = 0
    long_cases = 0
    for record in result.records:
        draft_post = str(record.input.get("draft_post", ""))
        if "\n\n" in draft_post:
            multiline_cases += 1
        if len(draft_post) >= 450:
            long_cases += 1

    assert multiline_cases >= 10
    assert long_cases >= 10
