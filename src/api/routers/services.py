from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import Response

from src.api.db.engine import get_session
from src.api.db.queries import (
    create_service,
    delete_service,
    get_service_by_id,
    get_services_for_business,
    update_service,
)
from src.api.dependencies import get_current_business_id
from src.api_schema.schemas import ServiceCreate, ServiceResponse, ServiceUpdate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/businesses/{business_id}/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    business_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> list[ServiceResponse]:
    services = await get_services_for_business(session, business_id)
    return [ServiceResponse.model_validate(s) for s in services]


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def add_service(
    business_id: uuid.UUID,
    body: ServiceCreate,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> ServiceResponse:
    service = await create_service(session, business_id=business_id, **body.model_dump())
    return ServiceResponse.model_validate(service)


@router.patch("/{service_id}", response_model=ServiceResponse)
async def patch_service(
    service_id: uuid.UUID,
    body: ServiceUpdate,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> ServiceResponse:
    service = await get_service_by_id(session, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    updated = await update_service(session, service, **body.model_dump(exclude_unset=True))
    return ServiceResponse.model_validate(updated)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def remove_service(
    service_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
):
    service = await get_service_by_id(session, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    await delete_service(session, service)
