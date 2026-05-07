"""Deterministic-компоненты для анализа и очистки AI-паттернов в постах."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def detect_ai_patterns(state: Any, _node: Any) -> dict[str, Any]:
    """Находит известные AI-паттерны в тексте и возвращает диагностические сигналы."""

    text = _extract_source_text(state)
    patterns = _load_ai_patterns()
    matches = _find_pattern_matches(text, patterns)
    unique_matches = sorted(set(matches))
    pattern_density = len(unique_matches)
    style_risk = "high" if pattern_density >= 3 else "low"
    return {
        "source_text": text,
        "ai_pattern_hits": unique_matches,
        "ai_pattern_density": pattern_density,
        "style_risk": style_risk,
    }


def strip_ai_patterns(state: Any, _node: Any) -> dict[str, Any]:
    """Убирает из текста наиболее частотные маркеры AI-стиля и возвращает очищенный черновик."""

    source_text = str(getattr(state, "payload", {}).get("source_text") or _extract_source_text(state))
    patterns = _load_ai_patterns()
    cleaned_text = source_text
    for pattern in patterns:
        phrase = str(pattern.get("pattern", "")).strip()
        if not phrase:
            continue
        cleaned_text = re.sub(re.escape(phrase), "", cleaned_text, flags=re.IGNORECASE)

    cleaned_text = re.sub(r"[ \t]{2,}", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
    return {"cleaned_text": cleaned_text}


def _extract_source_text(state: Any) -> str:
    """Извлекает исходный текст поста из payload с fallback на поле `query`."""

    payload = getattr(state, "payload", {})
    if not isinstance(payload, dict):
        return ""
    draft_post = payload.get("draft_post")
    if isinstance(draft_post, str) and draft_post.strip():
        return draft_post
    query = payload.get("query")
    if isinstance(query, str):
        return query
    return ""


def _find_pattern_matches(text: str, patterns: list[dict[str, Any]]) -> list[str]:
    """Ищет совпадения известных паттернов в тексте поста."""

    text_lower = text.lower()
    matches: list[str] = []
    for item in patterns:
        phrase = str(item.get("pattern", "")).strip()
        if phrase and phrase.lower() in text_lower:
            matches.append(phrase)
    return matches


def _load_ai_patterns() -> list[dict[str, Any]]:
    """Загружает справочник AI-паттернов из JSON-файла примеров."""

    project_root = Path(__file__).resolve().parents[1]
    patterns_file = project_root / "examples" / "resources" / "ai_style_patterns_ru_v1.json"
    raw_text = patterns_file.read_text(encoding="utf-8")
    payload = json.loads(raw_text)
    if not isinstance(payload, dict):
        return []
    patterns = payload.get("patterns")
    if not isinstance(patterns, list):
        return []
    return [item for item in patterns if isinstance(item, dict)]

