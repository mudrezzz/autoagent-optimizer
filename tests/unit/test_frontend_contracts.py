"""Unit-тесты контрактов frontend capability shell."""

from __future__ import annotations

import pytest

from optimizer.frontend.contracts import build_capability_catalog_payload, build_stub_capability_payload


def test_capability_catalog_contains_expected_items() -> None:
    """Проверяет, что capability-каталог содержит актуальные шаги wizard-модели."""

    payload = build_capability_catalog_payload()
    assert payload["version"] == "capability_catalog_v1"
    assert payload["ux_reference"] == "design_system/screenshots/app-v3.png"

    capabilities = payload["capabilities"]
    assert len(capabilities) == 9
    assert [item["id"] for item in capabilities] == ["c1", "c3", "c2", "c4", "c5", "c5s", "c6", "c7", "c8"]
    assert capabilities[0]["name"] == "Battle Registry"
    assert capabilities[0]["route"] == "/battles"


def test_capability_catalog_statuses_match_v2_4_scope() -> None:
    """Проверяет, что в текущем scope C1..C7 открыты, а C8 остается planned."""

    payload = build_capability_catalog_payload()
    capabilities = payload["capabilities"]
    statuses = {item["id"]: item["status"] for item in capabilities}

    assert statuses["c1"] == "enabled"
    assert statuses["c2"] == "enabled"
    assert statuses["c3"] == "enabled"
    assert statuses["c4"] == "enabled"
    assert statuses["c5"] == "enabled"
    assert statuses["c5s"] == "enabled"
    assert statuses["c6"] == "enabled"
    assert statuses["c7"] == "enabled"
    assert statuses["c8"] == "planned"


def test_stub_payload_contains_expected_shape() -> None:
    """Проверяет, что stub-payload содержит стабильный контракт полей для planned capability preview."""

    payload = build_stub_capability_payload("c8")
    assert payload["status"] == "stub_success"
    assert payload["capability_id"] == "c8"
    assert payload["capability_status"] == "planned"
    assert "summary" in payload
    assert "next_step" in payload


def test_stub_payload_raises_on_unknown_capability() -> None:
    """Проверяет fail-fast поведение для неизвестной capability в stub builder."""

    with pytest.raises(ValueError):
        build_stub_capability_payload("cx")
