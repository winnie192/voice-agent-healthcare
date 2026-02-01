from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from src.api.db.engine import get_session
from src.api.db.queries import get_call_logs_for_business
from src.api.dependencies import get_current_business_id
from src.api_schema.schemas import CallLogResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/businesses/{business_id}/call-logs", tags=["call-logs"])


@router.get("", response_model=list[CallLogResponse])
async def list_call_logs(
    business_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> list[CallLogResponse]:
    logs = await get_call_logs_for_business(session, business_id)
    return [CallLogResponse.model_validate(log) for log in logs]
