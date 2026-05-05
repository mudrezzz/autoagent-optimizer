"""Unit-тесты загрузки и валидации DSL-файлов."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.dsl.io import DslLoadError, DslValidationError, load_dsl_spec, load_yaml_payload


@pytest.mark.unit
def test_load_yaml_payload_raises_for_missing_file(tmp_path: Path) -> None:
    """Проверяет ошибку чтения для отсутствующего файла."""

    missing_path = tmp_path / "missing.yaml"
    with pytest.raises(DslLoadError):
        load_yaml_payload(missing_path)


@pytest.mark.unit
def test_load_yaml_payload_raises_for_invalid_yaml(tmp_path: Path) -> None:
    """Проверяет ошибку парсинга для невалидного YAML-содержимого."""

    file_path = tmp_path / "bad.yaml"
    file_path.write_text("project: [1,2\n", encoding="utf-8")
    with pytest.raises(DslLoadError):
        load_yaml_payload(file_path)


@pytest.mark.unit
def test_load_yaml_payload_raises_for_non_object_root(tmp_path: Path) -> None:
    """Проверяет, что верхний уровень YAML должен быть объектом."""

    file_path = tmp_path / "list_root.yaml"
    file_path.write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(DslLoadError):
        load_yaml_payload(file_path)


@pytest.mark.unit
def test_load_dsl_spec_raises_validation_for_incomplete_payload(tmp_path: Path) -> None:
    """Проверяет ошибку валидации, если обязательные поля DSL отсутствуют."""

    file_path = tmp_path / "incomplete.yaml"
    file_path.write_text("schema_version: '0.1'\nproject: {}\n", encoding="utf-8")
    with pytest.raises(DslValidationError):
        load_dsl_spec(file_path)

