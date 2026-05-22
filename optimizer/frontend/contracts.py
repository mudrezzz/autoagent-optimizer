"""Контракты capability-каталога и stub-ответов frontend shell."""

from __future__ import annotations

from typing import Any


# Русский комментарий: канонический список capability для Roadmap v2.
CAPABILITY_CATALOG: tuple[dict[str, str], ...] = (
    {"id": "c1", "name": "DSL/IR Studio", "description": "Валидация DSL и compile report в Graph IR."},
    {"id": "c2", "name": "Runtime Run", "description": "Запуск workflow и просмотр white-box trace."},
    {"id": "c3", "name": "Evaluation Profile", "description": "Profile-runner для dsl/native target."},
    {"id": "c4", "name": "Arena Ranking", "description": "Сравнение кандидатов, ranking и winner."},
    {"id": "c5", "name": "Evidence & Diagnostics", "description": "Comparative и diagnostic слои анализа."},
    {"id": "c6", "name": "Champion Bundle", "description": "Native-first экспорт и parity артефакты."},
)


def build_capability_catalog_payload() -> dict[str, Any]:
    """Возвращает API-payload каталога capability для frontend shell."""

    return {"version": "capability_catalog_v1", "capabilities": list(CAPABILITY_CATALOG)}


def build_stub_capability_payload(capability_id: str) -> dict[str, Any]:
    """Возвращает stub-payload capability, чтобы UI мог показать success-state до полной интеграции."""

    capability = next((item for item in CAPABILITY_CATALOG if item["id"] == capability_id), None)
    if capability is None:
        raise ValueError(f"Unknown capability_id: {capability_id}")

    return {
        "status": "stub_success",
        "capability_id": capability_id,
        "capability_name": capability["name"],
        "summary": f"Stub response for {capability['name']}.",
        "next_step": "Replace this stub with real endpoint logic in the next vertical slice.",
    }

