from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from src.api.db.engine import get_session
from src.api.db.queries import get_bookings_for_business
from src.api.dependencies import get_current_business_id
from src.api_schema.schemas import BookingResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/businesses/{business_id}/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
async def list_bookings(
    business_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> list[BookingResponse]:
    bookings = await get_bookings_for_business(session, business_id)
    return [BookingResponse.model_validate(b) for b in bookings]
