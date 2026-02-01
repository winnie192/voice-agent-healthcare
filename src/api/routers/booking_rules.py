from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.db.engine import get_session
from src.api.db.queries import get_booking_rules, upsert_booking_rules
from src.api.dependencies import get_current_business_id
from src.api_schema.schemas import BookingRuleResponse, BookingRuleUpdate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/businesses/{business_id}/booking-rules", tags=["booking-rules"])


@router.get("", response_model=BookingRuleResponse | None)
async def get_rules(
    business_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> BookingRuleResponse | None:
    rules = await get_booking_rules(session, business_id)
    if not rules:
        return None
    return BookingRuleResponse.model_validate(rules)


@router.put("", response_model=BookingRuleResponse)
async def set_rules(
    business_id: uuid.UUID,
    body: BookingRuleUpdate,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> BookingRuleResponse:
    rules = await upsert_booking_rules(session, business_id, **body.model_dump(exclude_unset=True))
    return BookingRuleResponse.model_validate(rules)
