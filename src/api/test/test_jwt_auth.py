from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt

from src.api.config import settings
from src.api.dependencies import get_current_business_id
from src.api.main import app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

BUSINESS_PAYLOAD = {
    "name": "JWT Test Clinic",
    "phone": "+15559001111",
    "admin_email": "jwttest@example.com",
    "admin_password": "securepass",
}


@pytest_asyncio.fixture
async def real_auth_client() -> AsyncGenerator[AsyncClient, None]:
    original = app.dependency_overrides.pop(get_current_business_id, None)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        if original is not None:
            app.dependency_overrides[get_current_business_id] = original


async def _register_and_login(client: AsyncClient) -> tuple[str, str]:
    resp = await client.post("/businesses", json=BUSINESS_PAYLOAD)
    biz_id = resp.json()["id"]
    login_resp = await client.post(
        "/auth/login",
        json={"email": "jwttest@example.com", "password": "securepass"},
    )
    token = login_resp.json()["access_token"]
    return biz_id, token


@pytest.mark.asyncio
async def test_real_jwt_token_grants_access(real_auth_client: AsyncClient) -> None:
    biz_id, token = await _register_and_login(real_auth_client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await real_auth_client.get(f"/businesses/{biz_id}/services", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_expired_jwt_token_rejected(real_auth_client: AsyncClient) -> None:
    from datetime import datetime, timedelta, timezone

    expired_payload = {
        "sub": str(uuid.uuid4()),
        "business_id": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    resp = await real_auth_client.get(
        f"/businesses/{uuid.uuid4()}/services", headers=headers
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid token"}


@pytest.mark.asyncio
async def test_wrong_secret_jwt_rejected(real_auth_client: AsyncClient) -> None:
    payload = {
        "sub": str(uuid.uuid4()),
        "business_id": str(uuid.uuid4()),
        "exp": 9999999999,
    }
    bad_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {bad_token}"}
    resp = await real_auth_client.get(
        f"/businesses/{uuid.uuid4()}/services", headers=headers
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_missing_business_id_in_jwt_rejected(
    real_auth_client: AsyncClient,
) -> None:
    payload = {
        "sub": str(uuid.uuid4()),
        "exp": 9999999999,
    }
    token = jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    headers = {"Authorization": f"Bearer {token}"}
    resp = await real_auth_client.get(
        f"/businesses/{uuid.uuid4()}/services", headers=headers
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_no_auth_header_rejected(real_auth_client: AsyncClient) -> None:
    resp = await real_auth_client.get(f"/businesses/{uuid.uuid4()}/services")
    assert resp.status_code == 403
