from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


async def _create_business(client: AsyncClient, suffix: str = "") -> str:
    resp = await client.post(
        "/businesses",
        json={
            "name": f"Svc Clinic {suffix}",
            "phone": f"+1555000{suffix.zfill(4)}",
            "admin_email": f"svc{suffix}@test.com",
            "admin_password": "pass123",
        },
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_and_list_services(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "1")
    headers = {"Authorization": "Bearer fake"}

    create_resp = await client.post(
        f"/businesses/{biz_id}/services",
        json={"name": "Checkup", "duration_minutes": 30, "price": 100.0},
        headers=headers,
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["name"] == "Checkup"

    list_resp = await client.get(f"/businesses/{biz_id}/services", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_service(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "2")
    headers = {"Authorization": "Bearer fake"}

    create_resp = await client.post(
        f"/businesses/{biz_id}/services",
        json={"name": "X-Ray", "duration_minutes": 15},
        headers=headers,
    )
    svc_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/businesses/{biz_id}/services/{svc_id}", headers=headers
    )
    assert del_resp.status_code == 204

    list_resp = await client.get(f"/businesses/{biz_id}/services", headers=headers)
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_patch_service(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "3")
    headers = {"Authorization": "Bearer fake"}

    create_resp = await client.post(
        f"/businesses/{biz_id}/services",
        json={"name": "Checkup", "duration_minutes": 30, "price": 100.0},
        headers=headers,
    )
    svc_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/businesses/{biz_id}/services/{svc_id}",
        json={"name": "Annual Checkup", "price": 150.0},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["name"] == "Annual Checkup"
    assert body["price"] == 150.0
    assert body["duration_minutes"] == 30


@pytest.mark.asyncio
async def test_patch_service_not_found(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "4")
    headers = {"Authorization": "Bearer fake"}
    import uuid

    fake_id = str(uuid.uuid4())
    resp = await client.patch(
        f"/businesses/{biz_id}/services/{fake_id}",
        json={"name": "Nope"},
        headers=headers,
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Service not found"}
