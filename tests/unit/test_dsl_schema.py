"""Unit-тесты typed-схемы DSL v0."""

from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from optimizer.dsl.schema import AutoAgentDslSpec


def _build_minimal_valid_payload() -> dict:
    """Создает минимально валидный payload DSL для unit-тестов."""

    return {
        "schema_version": "0.1",
        "project": {
            "id": "unit-project",
            "name": "Unit Project",
            "description": "Проверка DSL-схемы.",
        },
        "mission": {
            "task_type": "support_qa",
            "objective": "Проверить валидацию.",
            "success_definition": "Тест проходит.",
        },
        "constraints": {
            "max_cost_usd": 10,
            "max_latency_ms": 1000,
            "allowed_model_providers": ["openrouter"],
            "require_human_approval": False,
        },
        "datasets": [],
        "components": [
            {
                "id": "llm_node_component",
                "kind": "llm",
                "implementation": "provider://openrouter/openai/gpt-4o-mini",
            }
        ],
        "graph": {
            "entry_node": "n1",
            "nodes": [
                {
                    "id": "n1",
                    "type": "llm",
                    "component_id": "llm_node_component",
                    "prompt_id": "prompt_1",
                    "on_fail": "retry",
                }
            ],
            "edges": [
                {
                    "source": "n1",
                    "target": "n1",
                }
            ],
        },
        "metrics": [
            {
                "id": "task_success_rate",
                "kind": "output",
                "direction": "maximize",
                "description": "Доля успешных кейсов.",
            }
        ],
        "budget": {
            "max_trials": 2,
            "max_total_cost_usd": 10,
            "max_wall_time_minutes": 5,
        },
        "architecture_space": {
            "selection_policy": "equal_budget_tournament",
            "candidates": [
                {
                    "id": "baseline_1",
                    "template": "direct_llm",
                    "enabled": True,
                }
            ],
        },
    }


@pytest.mark.unit
def test_schema_accepts_minimal_valid_payload() -> None:
    """Проверяет, что минимально валидный payload проходит валидацию."""

    payload = _build_minimal_valid_payload()
    spec = AutoAgentDslSpec.model_validate(payload)
    assert spec.project.id == "unit-project"
    assert spec.graph.entry_node == "n1"


@pytest.mark.unit
def test_schema_rejects_duplicate_node_ids() -> None:
    """Проверяет, что схема отклоняет дубли идентификаторов узлов."""

    payload = _build_minimal_valid_payload()
    payload["graph"]["nodes"].append(deepcopy(payload["graph"]["nodes"][0]))
    with pytest.raises(ValidationError):
        AutoAgentDslSpec.model_validate(payload)


@pytest.mark.unit
def test_schema_rejects_missing_entry_node() -> None:
    """Проверяет, что `entry_node` обязан существовать среди узлов графа."""

    payload = _build_minimal_valid_payload()
    payload["graph"]["entry_node"] = "missing-node"
    with pytest.raises(ValidationError):
        AutoAgentDslSpec.model_validate(payload)


@pytest.mark.unit
def test_schema_rejects_missing_component_reference() -> None:
    """Проверяет, что узлы не могут ссылаться на отсутствующие компоненты."""

    payload = _build_minimal_valid_payload()
    payload["graph"]["nodes"][0]["component_id"] = "not-exists"
    with pytest.raises(ValidationError):
        AutoAgentDslSpec.model_validate(payload)

