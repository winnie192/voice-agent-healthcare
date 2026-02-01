from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.db.models import Base
from src.api.main import app
from src.api.db.engine import get_session
from src.api.dependencies import get_current_business_id

TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


FAKE_BUSINESS_ID = uuid.uuid4()


async def override_get_current_business_id() -> uuid.UUID:
    return FAKE_BUSINESS_ID


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_business_id] = override_get_current_business_id


@pytest_asyncio.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as s:
        yield s
