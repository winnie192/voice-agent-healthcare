from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from src.api.db.engine import get_session
from src.api.db.queries import (
    create_admin_user,
    create_business,
    get_business_by_id,
    update_business,
)
from src.api.dependencies import get_current_business_id
from src.api_schema.schemas import BusinessCreate, BusinessResponse, BusinessUpdate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/businesses", tags=["businesses"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def register_business(
    body: BusinessCreate,
    session: AsyncSession = Depends(get_session),
) -> BusinessResponse:
    business = await create_business(
        session,
        name=body.name,
        phone=body.phone,
        timezone=body.timezone,
        location=body.location,
        hours=body.hours,
        policies=body.policies,
    )
    await create_admin_user(
        session,
        business_id=business.id,
        email=body.admin_email,
        hashed_password=pwd_context.hash(body.admin_password),
    )
    return BusinessResponse.model_validate(business)


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> BusinessResponse:
    business = await get_business_by_id(session, business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return BusinessResponse.model_validate(business)


@router.patch("/{business_id}", response_model=BusinessResponse)
async def patch_business(
    business_id: uuid.UUID,
    body: BusinessUpdate,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> BusinessResponse:
    business = await get_business_by_id(session, business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    updates = body.model_dump(exclude_unset=True)
    updated = await update_business(session, business, **updates)
    return BusinessResponse.model_validate(updated)
