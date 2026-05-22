"""Контракты capability-каталога и stub-ответов frontend shell."""

from __future__ import annotations

from typing import Any


# Русский комментарий: канонический список capability для Roadmap v2 с UI-статусом.
CAPABILITY_CATALOG: tuple[dict[str, str | int], ...] = (
    {
        "id": "c1",
        "name": "DSL/IR Studio",
        "description": "Валидация DSL и compile report в Graph IR.",
        "status": "enabled",
        "route": "/workbench/c1",
        "badge_count": 1,
    },
    {
        "id": "c2",
        "name": "Runtime Run",
        "description": "Запуск workflow и просмотр white-box trace.",
        "status": "planned",
        "route": "/workbench/c2",
        "badge_count": 0,
    },
    {
        "id": "c3",
        "name": "Evaluation Profile",
        "description": "Profile-runner для dsl/native target.",
        "status": "planned",
        "route": "/workbench/c3",
        "badge_count": 0,
    },
    {
        "id": "c4",
        "name": "Arena Ranking",
        "description": "Сравнение кандидатов, ranking и winner.",
        "status": "planned",
        "route": "/workbench/c4",
        "badge_count": 0,
    },
    {
        "id": "c5",
        "name": "Evidence & Diagnostics",
        "description": "Comparative и diagnostic слои анализа.",
        "status": "planned",
        "route": "/workbench/c5",
        "badge_count": 0,
    },
    {
        "id": "c6",
        "name": "Champion Bundle",
        "description": "Native-first экспорт и parity артефакты.",
        "status": "planned",
        "route": "/workbench/c6",
        "badge_count": 0,
    },
)


def build_capability_catalog_payload() -> dict[str, Any]:
    """Возвращает API-payload каталога capability для frontend shell."""

    # Русский комментарий: payload содержит UX-снимок статусов для capability-driven интерфейса.
    return {
        "version": "capability_catalog_v1",
        "ux_reference": "design_system/screenshots/app-v3.png",
        "capabilities": list(CAPABILITY_CATALOG),
    }


def build_stub_capability_payload(capability_id: str) -> dict[str, Any]:
    """Возвращает stub-payload capability, чтобы UI мог показать planned-state до полной интеграции."""

    capability = next((item for item in CAPABILITY_CATALOG if item["id"] == capability_id), None)
    if capability is None:
        raise ValueError(f"Unknown capability_id: {capability_id}")

    return {
        "status": "stub_success",
        "capability_id": capability_id,
        "capability_name": capability["name"],
        "capability_status": capability["status"],
        "summary": f"Stub response for {capability['name']}.",
        "next_step": "Replace this stub with real endpoint logic in the next vertical slice.",
    }
