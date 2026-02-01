from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

BUSINESS_PAYLOAD = {
    "name": "Auth Test Clinic",
    "phone": "+15550001111",
    "admin_email": "authtest@example.com",
    "admin_password": "correctpassword",
}


async def _register_business(client: AsyncClient) -> str:
    resp = await client.post("/businesses", json=BUSINESS_PAYLOAD)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await _register_business(client)
    resp = await client.post(
        "/auth/login",
        json={"email": "authtest@example.com", "password": "correctpassword"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await _register_business(client)
    resp = await client.post(
        "/auth/login",
        json={"email": "authtest@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid credentials"}


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "anything"},
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid credentials"}
