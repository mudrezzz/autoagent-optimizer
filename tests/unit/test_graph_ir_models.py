"""Unit-тесты моделей и валидаторов Graph IR."""

from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from optimizer.graph_ir.models import GraphIRSpec


def _build_valid_graph_ir_payload() -> dict:
    """Создает минимально валидный payload Graph IR для unit-тестов."""

    return {
        "ir_version": "0.1",
        "entry_node": "n_start",
        "terminal_nodes": ["n_end"],
        "nodes": [
            {
                "id": "n_start",
                "kind": "llm",
                "component_ref": "component://intent_router",
                "config": {},
                "on_fail": "retry",
            },
            {
                "id": "n_end",
                "kind": "validator",
                "component_ref": "component://schema_guard",
                "config": {},
                "on_fail": "stop",
            },
        ],
        "edges": [
            {
                "source": "n_start",
                "target": "n_end",
                "condition": None,
                "label": "main",
            }
        ],
        "metadata": {},
    }


@pytest.mark.unit
def test_graph_ir_accepts_valid_payload() -> None:
    """Проверяет, что валидный payload успешно проходит валидацию."""

    spec = GraphIRSpec.model_validate(_build_valid_graph_ir_payload())
    assert spec.entry_node == "n_start"
    assert spec.terminal_nodes == ["n_end"]


@pytest.mark.unit
def test_graph_ir_rejects_unreachable_node() -> None:
    """Проверяет, что схема отклоняет недостижимый узел."""

    payload = _build_valid_graph_ir_payload()
    payload["nodes"].append(
        {
            "id": "n_unreachable",
            "kind": "tool",
            "component_ref": "component://tool",
            "config": {},
            "on_fail": "stop",
        }
    )
    with pytest.raises(ValidationError):
        GraphIRSpec.model_validate(payload)


@pytest.mark.unit
def test_graph_ir_rejects_terminal_with_outgoing_edge() -> None:
    """Проверяет, что терминальный узел не может иметь исходящие ребра."""

    payload = _build_valid_graph_ir_payload()
    payload["edges"].append(
        {
            "source": "n_end",
            "target": "n_start",
            "condition": None,
            "label": "invalid_back_edge",
        }
    )
    with pytest.raises(ValidationError):
        GraphIRSpec.model_validate(payload)


@pytest.mark.unit
def test_graph_ir_rejects_non_terminal_without_outgoing_edge() -> None:
    """Проверяет, что не-терминальный узел обязан иметь исходящее ребро."""

    payload = _build_valid_graph_ir_payload()
    payload["nodes"].insert(
        1,
        {
            "id": "n_mid",
            "kind": "deterministic",
            "component_ref": "component://mid",
            "config": {},
            "on_fail": "stop",
        },
    )
    with pytest.raises(ValidationError):
        GraphIRSpec.model_validate(payload)


@pytest.mark.unit
def test_graph_ir_rejects_terminal_node_missing_in_nodes() -> None:
    """Проверяет, что terminal_nodes должен ссылаться на существующие узлы."""

    payload = _build_valid_graph_ir_payload()
    payload["terminal_nodes"] = ["missing_terminal"]
    with pytest.raises(ValidationError):
        GraphIRSpec.model_validate(payload)


@pytest.mark.unit
def test_graph_ir_roundtrip_preserves_structure() -> None:
    """Проверяет сериализацию/десериализацию Graph IR без потери структуры."""

    payload = _build_valid_graph_ir_payload()
    payload_copy = deepcopy(payload)
    spec = GraphIRSpec.model_validate(payload_copy)
    restored = GraphIRSpec.model_validate_json(spec.model_dump_json())
    assert restored.model_dump(mode="json") == spec.model_dump(mode="json")

