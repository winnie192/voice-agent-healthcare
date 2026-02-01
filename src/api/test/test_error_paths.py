from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

AUTH_HEADERS = {"Authorization": "Bearer fake"}


@pytest.mark.asyncio
async def test_get_nonexistent_business(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/businesses/{fake_id}", headers=AUTH_HEADERS)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Business not found"}


@pytest.mark.asyncio
async def test_patch_nonexistent_business(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    resp = await client.patch(
        f"/businesses/{fake_id}",
        json={"name": "Ghost"},
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Business not found"}


@pytest.mark.asyncio
async def test_patch_nonexistent_service(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    resp = await client.patch(
        f"/businesses/{fake_id}/services/{uuid.uuid4()}",
        json={"name": "Nope"},
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Service not found"}


@pytest.mark.asyncio
async def test_delete_nonexistent_service(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    resp = await client.delete(
        f"/businesses/{fake_id}/services/{uuid.uuid4()}",
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Service not found"}


@pytest.mark.asyncio
async def test_invalid_uuid_returns_422(client: AsyncClient) -> None:
    resp = await client.get("/businesses/not-a-uuid", headers=AUTH_HEADERS)
    assert resp.status_code == 422
