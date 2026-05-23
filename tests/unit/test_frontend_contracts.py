"""Unit-тесты контрактов frontend capability shell."""

from __future__ import annotations

import pytest

from optimizer.frontend.contracts import build_capability_catalog_payload, build_stub_capability_payload


def test_capability_catalog_contains_six_items() -> None:
    """Проверяет, что capability-каталог содержит ровно шесть обязательных направлений C1..C6."""

    payload = build_capability_catalog_payload()
    assert payload["version"] == "capability_catalog_v1"
    assert payload["ux_reference"] == "design_system/screenshots/app-v3.png"

    capabilities = payload["capabilities"]
    assert len(capabilities) == 6
    assert [item["id"] for item in capabilities] == ["c1", "c2", "c3", "c4", "c5", "c6"]
    assert capabilities[0]["name"] == "Battle Registry"
    assert capabilities[0]["route"] == "/battles"


def test_capability_catalog_statuses_match_v2_3_s2_scope() -> None:
    """Проверяет, что в V2.3.S2 capability C1 и C2 открыты как enabled."""

    payload = build_capability_catalog_payload()
    capabilities = payload["capabilities"]
    statuses = {item["id"]: item["status"] for item in capabilities}

    assert statuses["c1"] == "enabled"
    assert statuses["c2"] == "enabled"
    assert statuses["c3"] == "planned"
    assert statuses["c4"] == "planned"
    assert statuses["c5"] == "planned"
    assert statuses["c6"] == "planned"


def test_stub_payload_contains_expected_shape() -> None:
    """Проверяет, что stub-payload содержит стабильный контракт полей для planned capability preview."""

    payload = build_stub_capability_payload("c4")
    assert payload["status"] == "stub_success"
    assert payload["capability_id"] == "c4"
    assert payload["capability_status"] == "planned"
    assert "summary" in payload
    assert "next_step" in payload


def test_stub_payload_raises_on_unknown_capability() -> None:
    """Проверяет fail-fast поведение для неизвестной capability в stub builder."""

    with pytest.raises(ValueError):
        build_stub_capability_payload("cx")
