"""Unit-тесты контрактов frontend capability shell."""

from __future__ import annotations

import pytest

from optimizer.frontend.contracts import build_capability_catalog_payload, build_stub_capability_payload


def test_capability_catalog_contains_six_items() -> None:
    """Проверяет, что capability-каталог содержит ровно шесть обязательных направлений C1..C6."""

    payload = build_capability_catalog_payload()
    assert payload["version"] == "capability_catalog_v1"
    capabilities = payload["capabilities"]
    assert len(capabilities) == 6
    assert [item["id"] for item in capabilities] == ["c1", "c2", "c3", "c4", "c5", "c6"]


def test_stub_payload_contains_expected_shape() -> None:
    """Проверяет, что stub-payload содержит стабильный контракт полей для frontend success-state."""

    payload = build_stub_capability_payload("c4")
    assert payload["status"] == "stub_success"
    assert payload["capability_id"] == "c4"
    assert "summary" in payload
    assert "next_step" in payload


def test_stub_payload_raises_on_unknown_capability() -> None:
    """Проверяет fail-fast поведение для неизвестной capability в stub builder."""

    with pytest.raises(ValueError):
        build_stub_capability_payload("cx")

