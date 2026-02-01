from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

AUTH_HEADERS = {"Authorization": "Bearer fake"}


async def _create_business(client: AsyncClient, suffix: str = "kb") -> str:
    resp = await client.post(
        "/businesses",
        json={
            "name": f"KB Clinic {suffix}",
            "phone": f"+1555300{suffix.zfill(4)}",
            "admin_email": f"kb{suffix}@test.com",
            "admin_password": "pass123",
        },
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_documents_empty(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "empty")
    resp = await client.get(
        f"/businesses/{biz_id}/knowledge-base", headers=AUTH_HEADERS
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_and_list_document(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "crdoc")
    doc_payload = {"title": "Office Policies", "content": "No walk-ins after 5 PM."}
    create_resp = await client.post(
        f"/businesses/{biz_id}/knowledge-base",
        json=doc_payload,
        headers=AUTH_HEADERS,
    )
    assert create_resp.status_code == 201
    data = create_resp.json()
    assert data["title"] == "Office Policies"
    assert data["content"] == "No walk-ins after 5 PM."
    assert data["business_id"] == biz_id

    list_resp = await client.get(
        f"/businesses/{biz_id}/knowledge-base", headers=AUTH_HEADERS
    )
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "deldoc")
    create_resp = await client.post(
        f"/businesses/{biz_id}/knowledge-base",
        json={"title": "Temp Doc", "content": "Will be deleted."},
        headers=AUTH_HEADERS,
    )
    doc_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/businesses/{biz_id}/knowledge-base/{doc_id}", headers=AUTH_HEADERS
    )
    assert del_resp.status_code == 204

    list_resp = await client.get(
        f"/businesses/{biz_id}/knowledge-base", headers=AUTH_HEADERS
    )
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client: AsyncClient) -> None:
    biz_id = await _create_business(client, "delnon")
    fake_id = str(uuid.uuid4())
    resp = await client.delete(
        f"/businesses/{biz_id}/knowledge-base/{fake_id}", headers=AUTH_HEADERS
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Document not found"}
