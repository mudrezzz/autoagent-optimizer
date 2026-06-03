"""Каталог evaluator-adapters и правила совместимости с метриками."""

from __future__ import annotations

import os
from typing import Any


# Русский комментарий: v0-каталог описывает не исполнение evaluator-а, а его продуктовый контракт.
_EVALUATOR_ADAPTER_CATALOG: dict[str, dict[str, Any]] = {
    "golden_oracle": {
        "evaluator_id": "golden_oracle",
        "adapter_kind": "golden_dataset",
        "title": "Golden dataset oracle",
        "description": "Deterministic evaluator that compares agent output with expected dataset payload.",
        "requires_dataset": True,
        "requires_llm": False,
        "requires_stage_mapping": False,
        "supported_metric_refs": [
            "comparative:quality_f1",
            "diagnostic:retrieval_coverage",
            "diagnostic:rerank_gain",
            "diagnostic:synthesis_drift",
        ],
        "budget_cost_model": "cases",
        "adapter_status": "available",
        "adapter_status_reason": "",
    },
    "llm_judge": {
        "evaluator_id": "llm_judge",
        "adapter_kind": "llm_judge",
        "title": "LLM as a judge",
        "description": "Semantic judge for style, faithfulness and output quality checks.",
        "requires_dataset": False,
        "requires_llm": True,
        "requires_stage_mapping": False,
        "supported_metric_refs": [
            "comparative:quality_f1",
            "diagnostic:synthesis_drift",
        ],
        "budget_cost_model": "llm_calls",
        "adapter_status": "available",
        "adapter_status_reason": "",
    },
    "executable_validator": {
        "evaluator_id": "executable_validator",
        "adapter_kind": "executable",
        "title": "Executable validator",
        "description": "Code/test/render checks that can validate deterministic properties.",
        "requires_dataset": False,
        "requires_llm": False,
        "requires_stage_mapping": False,
        "supported_metric_refs": [
            "comparative:cost_per_case",
            "comparative:latency_p95",
        ],
        "budget_cost_model": "runtime",
        "adapter_status": "available",
        "adapter_status_reason": "",
    },
    "render_validator": {
        "evaluator_id": "render_validator",
        "adapter_kind": "render",
        "title": "Render validator",
        "description": "Visual/render checks for UI, document and artifact generation tasks.",
        "requires_dataset": False,
        "requires_llm": False,
        "requires_stage_mapping": False,
        "supported_metric_refs": [],
        "budget_cost_model": "runtime",
        "adapter_status": "planned",
        "adapter_status_reason": "Render evaluator execution is planned after adapter contract v0.",
    },
}


def build_evaluator_adapter_catalog() -> list[dict[str, Any]]:
    """Возвращает публичный каталог evaluator-adapters для API/UI."""

    return [enrich_evaluator_adapter({"evaluator_id": evaluator_id, "enabled": False}) for evaluator_id in sorted(_EVALUATOR_ADAPTER_CATALOG)]


def enrich_evaluator_adapter(raw_evaluator: dict[str, Any]) -> dict[str, Any]:
    """Обогащает evaluator сохраненным состоянием и metadata из adapter catalog."""

    evaluator_id = str(raw_evaluator.get("evaluator_id", "")).strip()
    catalog_item = dict(_EVALUATOR_ADAPTER_CATALOG.get(evaluator_id, {}))
    if not catalog_item:
        catalog_item = _build_custom_evaluator_adapter(raw_evaluator)

    adapter_status = str(catalog_item.get("adapter_status", "available")).strip() or "available"
    adapter_status_reason = str(catalog_item.get("adapter_status_reason", "")).strip()
    if bool(catalog_item.get("requires_llm", False)) and not _has_openrouter_api_key():
        adapter_status = "needs_config"
        adapter_status_reason = "OPENROUTER_API_KEY is required for this evaluator."

    supported_metric_refs = _normalize_metric_refs(catalog_item.get("supported_metric_refs", []))
    return {
        "evaluator_id": str(catalog_item.get("evaluator_id", evaluator_id)).strip() or evaluator_id,
        "adapter_kind": str(catalog_item.get("adapter_kind", "custom")).strip() or "custom",
        "title": str(raw_evaluator.get("title", catalog_item.get("title", evaluator_id))).strip() or evaluator_id,
        "description": str(raw_evaluator.get("description", catalog_item.get("description", ""))).strip(),
        "enabled": bool(raw_evaluator.get("enabled", False)),
        "requires_dataset": bool(catalog_item.get("requires_dataset", False)),
        "requires_llm": bool(catalog_item.get("requires_llm", False)),
        "requires_stage_mapping": bool(catalog_item.get("requires_stage_mapping", False)),
        "supported_metric_refs": supported_metric_refs,
        "supported_metric_kinds": _resolve_supported_metric_kinds(supported_metric_refs),
        "budget_cost_model": str(catalog_item.get("budget_cost_model", "runtime")).strip() or "runtime",
        "adapter_status": adapter_status,
        "adapter_status_reason": adapter_status_reason,
    }


def evaluate_evaluator_metric_compatibility(
    *,
    evaluator: dict[str, Any],
    metric_kind: str,
    metric_id: str,
) -> dict[str, str]:
    """Возвращает verdict совместимости evaluator-а с конкретной metric-ref."""

    normalized_kind = str(metric_kind).strip().lower()
    normalized_metric_id = str(metric_id).strip()
    metric_ref = f"{normalized_kind}:{normalized_metric_id}"
    supported_metric_refs = set(_normalize_metric_refs(evaluator.get("supported_metric_refs", [])))
    adapter_status = str(evaluator.get("adapter_status", "available")).strip() or "available"
    if adapter_status == "planned":
        return {
            "compatibility_status": "incompatible",
            "compatibility_reason": "Evaluator adapter is planned and cannot be used yet.",
        }
    if metric_ref not in supported_metric_refs:
        return {
            "compatibility_status": "incompatible",
            "compatibility_reason": f"{evaluator.get('title', evaluator.get('evaluator_id', 'Evaluator'))} does not support {metric_ref}.",
        }
    return {"compatibility_status": "compatible", "compatibility_reason": ""}


def _build_custom_evaluator_adapter(raw_evaluator: dict[str, Any]) -> dict[str, Any]:
    """Строит conservative metadata для неизвестного evaluator-а из пользовательского payload."""

    evaluator_id = str(raw_evaluator.get("evaluator_id", "")).strip() or "custom_evaluator"
    return {
        "evaluator_id": evaluator_id,
        "adapter_kind": str(raw_evaluator.get("adapter_kind", "custom")).strip() or "custom",
        "title": str(raw_evaluator.get("title", evaluator_id)).strip() or evaluator_id,
        "description": str(raw_evaluator.get("description", "")).strip(),
        "requires_dataset": bool(raw_evaluator.get("requires_dataset", False)),
        "requires_llm": bool(raw_evaluator.get("requires_llm", False)),
        "requires_stage_mapping": bool(raw_evaluator.get("requires_stage_mapping", False)),
        "supported_metric_refs": _normalize_metric_refs(raw_evaluator.get("supported_metric_refs", [])),
        "budget_cost_model": str(raw_evaluator.get("budget_cost_model", "runtime")).strip() or "runtime",
        "adapter_status": str(raw_evaluator.get("adapter_status", "available")).strip() or "available",
        "adapter_status_reason": str(raw_evaluator.get("adapter_status_reason", "")).strip(),
    }


def _normalize_metric_refs(raw_refs: Any) -> list[str]:
    """Нормализует список metric refs формата `kind:id`."""

    if not isinstance(raw_refs, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_refs:
        if not isinstance(item, str):
            continue
        value = item.strip().lower()
        if ":" not in value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _resolve_supported_metric_kinds(metric_refs: list[str]) -> list[str]:
    """Выводит список типов метрик из полного списка поддерживаемых metric refs."""

    kinds: list[str] = []
    seen: set[str] = set()
    for metric_ref in metric_refs:
        kind = metric_ref.split(":", 1)[0]
        if not kind or kind in seen:
            continue
        seen.add(kind)
        kinds.append(kind)
    return kinds


def _has_openrouter_api_key() -> bool:
    """Проверяет наличие OpenRouter key без раскрытия значения секрета."""

    return bool(str(os.environ.get("OPENROUTER_API_KEY", "")).strip())
