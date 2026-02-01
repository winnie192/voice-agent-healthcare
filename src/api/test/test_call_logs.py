from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

AUTH_HEADERS = {"Authorization": "Bearer fake"}


async def _create_business(client: AsyncClient, suffix: str = "cl") -> str:
    resp = await client.post(
        "/businesses",
        json={
            "name": f"CallLog Clinic {suffix}",
            "phone": f"+1555500{suffix.zfill(4)}",
            "admin_email": f"cl{suffix}@test.com",
            "admin_password": "pass123",
        },
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_call_logs_empty(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "empty")
    resp = await client.get(
        f"/businesses/{biz_id}/call-logs", headers=AUTH_HEADERS
    )
    assert resp.status_code == 200
    assert resp.json() == []
