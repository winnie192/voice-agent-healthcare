from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest

from src.api.db.queries import create_booking, create_business, create_service

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

AUTH_HEADERS = {"Authorization": "Bearer fake"}


async def _create_business(client: AsyncClient, suffix: str = "bk") -> str:
    resp = await client.post(
        "/businesses",
        json={
            "name": f"Booking Clinic {suffix}",
            "phone": f"+1555400{suffix.zfill(4)}",
            "admin_email": f"bk{suffix}@test.com",
            "admin_password": "pass123",
        },
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_bookings_empty(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "empty")
    resp = await client.get(f"/businesses/{biz_id}/bookings", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_booking_via_query_and_list(
    client: AsyncClient, session: AsyncSession
) -> None:

    business = await create_business(
        session,
        name="Booking Direct Clinic",
        phone="+15556661234",
        timezone="UTC",
    )
    service = await create_service(
        session,
        business_id=business.id,
        name="Consultation",
        duration_minutes=30,
    )
    now = datetime.now(timezone.utc)
    booking = await create_booking(
        session,
        business_id=business.id,
        service_id=service.id,
        customer_name="Jane Doe",
        customer_phone="+15550001234",
        start_time=now,
        end_time=now + timedelta(minutes=30),
        status="confirmed",
    )

    resp = await client.get(f"/businesses/{business.id}/bookings", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(booking.id)
    assert data[0]["customer_name"] == "Jane Doe"
    assert data[0]["status"] == "confirmed"
    assert data[0]["service_id"] == str(service.id)
