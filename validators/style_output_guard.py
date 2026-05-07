"""Валидатор стилистической правки постов с базовой диагностикой AI-лейксигнала."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def validate(state: Any, _node: Any) -> dict[str, Any]:
    """Проверяет, что выходной текст непустой, и считает остаточный риск AI-паттернов."""

    payload = getattr(state, "payload", {})
    if not isinstance(payload, dict):
        return {"valid": False, "style_risk": "high", "reason": "payload is not dict"}

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return {"valid": False, "style_risk": "high", "reason": "text is empty"}

    patterns = _load_ai_patterns()
    matched = [phrase for phrase in patterns if phrase.lower() in text.lower()]
    style_risk = "high" if len(matched) >= 2 else "low"
    return {
        "valid": True,
        "style_risk": style_risk,
        "remaining_ai_patterns": matched[:5],
    }


def _load_ai_patterns() -> list[str]:
    """Загружает плоский список фраз AI-паттернов из JSON-справочника."""

    project_root = Path(__file__).resolve().parents[1]
    patterns_file = project_root / "examples" / "resources" / "ai_style_patterns_ru_v1.json"
    payload = json.loads(patterns_file.read_text(encoding="utf-8"))
    raw_patterns = payload.get("patterns", []) if isinstance(payload, dict) else []
    return [str(item.get("pattern", "")).strip() for item in raw_patterns if isinstance(item, dict)]

