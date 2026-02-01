from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

AUTH_HEADERS = {"Authorization": "Bearer fake"}


async def _create_business(client: AsyncClient, suffix: str = "br") -> str:
    resp = await client.post(
        "/businesses",
        json={
            "name": f"BookingRule Clinic {suffix}",
            "phone": f"+1555200{suffix.zfill(4)}",
            "admin_email": f"br{suffix}@test.com",
            "admin_password": "pass123",
        },
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_get_booking_rules_empty(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "empty")
    resp = await client.get(
        f"/businesses/{biz_id}/booking-rules", headers=AUTH_HEADERS
    )
    assert resp.status_code == 200
    assert resp.json() is None


@pytest.mark.asyncio
async def test_set_and_get_booking_rules(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "setget")
    rule_payload = {
        "advance_notice_hours": 12,
        "max_advance_days": 60,
        "cancellation_hours": 48,
        "allowed_days": ["Monday", "Wednesday", "Friday"],
    }
    put_resp = await client.put(
        f"/businesses/{biz_id}/booking-rules",
        json=rule_payload,
        headers=AUTH_HEADERS,
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["advance_notice_hours"] == 12
    assert data["max_advance_days"] == 60
    assert data["cancellation_hours"] == 48
    assert data["allowed_days"] == ["Monday", "Wednesday", "Friday"]
    assert data["business_id"] == biz_id

    get_resp = await client.get(
        f"/businesses/{biz_id}/booking-rules", headers=AUTH_HEADERS
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["advance_notice_hours"] == 12


@pytest.mark.asyncio
async def test_upsert_booking_rules_updates_existing(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "upsert")
    await client.put(
        f"/businesses/{biz_id}/booking-rules",
        json={"advance_notice_hours": 6},
        headers=AUTH_HEADERS,
    )
    update_resp = await client.put(
        f"/businesses/{biz_id}/booking-rules",
        json={"advance_notice_hours": 24},
        headers=AUTH_HEADERS,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["advance_notice_hours"] == 24
