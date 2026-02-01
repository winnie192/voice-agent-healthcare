from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_business(client: AsyncClient) -> None:
    payload = {
        "name": "Test Clinic",
        "phone": "+15551234567",
        "timezone": "America/New_York",
        "admin_email": "admin@test.com",
        "admin_password": "securepass123",
    }
    response = await client.post("/businesses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Clinic"
    assert data["phone"] == "+15551234567"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_business(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/businesses",
        json={
            "name": "Get Clinic",
            "phone": "+15559999999",
            "admin_email": "get@test.com",
            "admin_password": "pass123",
        },
    )
    business_id = create_resp.json()["id"]

    response = await client.get(
        f"/businesses/{business_id}",
        headers={"Authorization": "Bearer fake"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Get Clinic"


@pytest.mark.asyncio
async def test_patch_business(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/businesses",
        json={
            "name": "Patch Clinic",
            "phone": "+15558888888",
            "admin_email": "patch@test.com",
            "admin_password": "pass123",
        },
    )
    business_id = create_resp.json()["id"]

    response = await client.patch(
        f"/businesses/{business_id}",
        json={"name": "Updated Clinic"},
        headers={"Authorization": "Bearer fake"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Clinic"
