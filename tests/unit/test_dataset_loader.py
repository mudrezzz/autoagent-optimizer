"""Unit-тесты загрузчика и схемы golden dataset."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.evaluation.dataset_loader import GoldenDatasetLoader, GoldenDatasetLoadError


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_dataset_loader_loads_valid_dataset() -> None:
    """Проверяет успешную загрузку эталонного golden dataset."""

    loader = GoldenDatasetLoader()
    dataset_file = _project_root() / "examples" / "datasets" / "golden_support_v1.jsonl"
    result = loader.load_file(dataset_file)
    assert result.is_success is True
    assert len(result.records) == 3
    summary = result.summary()
    assert summary.records_total == 3
    assert summary.unique_case_ids == 3
    assert summary.tags_total >= 3


@pytest.mark.unit
def test_dataset_loader_reports_duplicate_case_id(tmp_path: Path) -> None:
    """Проверяет детекцию дублированного case_id в JSONL."""

    dataset_file = tmp_path / "dup.jsonl"
    dataset_file.write_text(
        "\n".join(
            [
                '{"case_id":"c1","input":{"x":1},"expected":{"y":1}}',
                '{"case_id":"c1","input":{"x":2},"expected":{"y":2}}',
            ]
        ),
        encoding="utf-8",
    )
    loader = GoldenDatasetLoader()
    result = loader.load_file(dataset_file)
    assert result.is_success is False
    assert any("Дубликат case_id" in issue.message for issue in result.issues)


@pytest.mark.unit
def test_dataset_loader_reports_json_and_schema_errors(tmp_path: Path) -> None:
    """Проверяет накопление ошибок JSON-парсинга и schema-валидации."""

    dataset_file = tmp_path / "bad.jsonl"
    dataset_file.write_text(
        "\n".join(
            [
                '{"case_id":"ok-1","input":{"x":1},"expected":{"y":1}}',
                '{"case_id":"broken-json","input":{"x":1},"expected":{"y":1}',
                '{"case_id":"","input":{},"expected":{}}',
            ]
        ),
        encoding="utf-8",
    )
    loader = GoldenDatasetLoader()
    result = loader.load_file(dataset_file)
    assert result.is_success is False
    assert len(result.issues) >= 2
    assert any("JSON parsing error" in issue.message for issue in result.issues)


@pytest.mark.unit
def test_dataset_loader_fails_for_missing_file(tmp_path: Path) -> None:
    """Проверяет ошибку загрузки при отсутствии dataset-файла."""

    loader = GoldenDatasetLoader()
    with pytest.raises(GoldenDatasetLoadError):
        loader.load_file(tmp_path / "missing.jsonl")

