"""Контракты capability-каталога и stub-ответов frontend shell."""

from __future__ import annotations

from typing import Any


# Русский комментарий: канонический список capability для Roadmap v3 с UI-статусом.
CAPABILITY_CATALOG: tuple[dict[str, str | int], ...] = (
    {
        "id": "c1",
        "name": "Battle Registry",
        "description": "Управление battle-аренами как входной точкой продукта.",
        "status": "enabled",
        "route": "/battles",
        "badge_count": 1,
    },
    {
        "id": "c2",
        "name": "Task Chat + Candidates",
        "description": "Постановка задачи в чате и генерация кандидатов.",
        "status": "enabled",
        "route": "/battles/chat",
        "badge_count": 1,
    },
    {
        "id": "c3",
        "name": "Pattern Library + RAG",
        "description": "Поиск и выбор архитектурных паттернов для кандидатов.",
        "status": "planned",
        "route": "/patterns",
        "badge_count": 0,
    },
    {
        "id": "c4",
        "name": "Dataset & Metrics Studio",
        "description": "Управление датасетами, метриками и методами оценки.",
        "status": "planned",
        "route": "/datasets",
        "badge_count": 0,
    },
    {
        "id": "c5",
        "name": "Optimizer Run Monitor",
        "description": "Запуск оптимизации и мониторинг эпох, логов и метрик.",
        "status": "planned",
        "route": "/runs",
        "badge_count": 0,
    },
    {
        "id": "c6",
        "name": "Report + Champion Export/Import",
        "description": "Финальный отчет, выбор победителя и native loop.",
        "status": "planned",
        "route": "/champion",
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
