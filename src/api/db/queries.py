from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import (
    AdminUser,
    Booking,
    BookingRule,
    Business,
    CallLog,
    KnowledgeBaseDocument,
    Service,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


async def get_business_by_id(session: AsyncSession, business_id: uuid.UUID) -> Business | None:
    return await session.get(Business, business_id)


async def get_business_by_phone(session: AsyncSession, phone: str) -> Business | None:
    result = await session.execute(select(Business).where(Business.phone == phone))
    return result.scalar_one_or_none()


async def create_business(session: AsyncSession, **kwargs: Any) -> Business:
    business = Business(**kwargs)
    session.add(business)
    await session.commit()
    await session.refresh(business)
    return business


async def update_business(session: AsyncSession, business: Business, **kwargs: Any) -> Business:
    for key, value in kwargs.items():
        setattr(business, key, value)
    await session.commit()
    await session.refresh(business)
    return business


async def get_admin_user_by_email(session: AsyncSession, email: str) -> AdminUser | None:
    result = await session.execute(select(AdminUser).where(AdminUser.email == email))
    return result.scalar_one_or_none()


async def create_admin_user(session: AsyncSession, **kwargs: Any) -> AdminUser:
    user = AdminUser(**kwargs)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_services_for_business(session: AsyncSession, business_id: uuid.UUID) -> Sequence[Service]:
    result = await session.execute(select(Service).where(Service.business_id == business_id))
    return result.scalars().all()


async def get_service_by_id(session: AsyncSession, service_id: uuid.UUID) -> Service | None:
    return await session.get(Service, service_id)


async def create_service(session: AsyncSession, **kwargs: Any) -> Service:
    service = Service(**kwargs)
    session.add(service)
    await session.commit()
    await session.refresh(service)
    return service


async def update_service(session: AsyncSession, service: Service, **kwargs: Any) -> Service:
    for key, value in kwargs.items():
        setattr(service, key, value)
    await session.commit()
    await session.refresh(service)
    return service


async def delete_service(session: AsyncSession, service: Service) -> None:
    await session.delete(service)
    await session.commit()


async def get_booking_rules(session: AsyncSession, business_id: uuid.UUID) -> BookingRule | None:
    result = await session.execute(select(BookingRule).where(BookingRule.business_id == business_id))
    return result.scalar_one_or_none()


async def upsert_booking_rules(session: AsyncSession, business_id: uuid.UUID, **kwargs: Any) -> BookingRule:
    existing = await get_booking_rules(session, business_id)
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
        await session.commit()
        await session.refresh(existing)
        return existing
    rule = BookingRule(business_id=business_id, **kwargs)
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


async def get_bookings_for_business(session: AsyncSession, business_id: uuid.UUID) -> Sequence[Booking]:
    result = await session.execute(
        select(Booking).where(Booking.business_id == business_id).order_by(Booking.start_time.desc())
    )
    return result.scalars().all()


async def create_booking(session: AsyncSession, **kwargs: Any) -> Booking:
    booking = Booking(**kwargs)
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


async def get_documents_for_business(session: AsyncSession, business_id: uuid.UUID) -> Sequence[KnowledgeBaseDocument]:
    result = await session.execute(
        select(KnowledgeBaseDocument).where(KnowledgeBaseDocument.business_id == business_id)
    )
    return result.scalars().all()


async def get_document_by_id(session: AsyncSession, doc_id: uuid.UUID) -> KnowledgeBaseDocument | None:
    return await session.get(KnowledgeBaseDocument, doc_id)


async def create_document(session: AsyncSession, **kwargs: Any) -> KnowledgeBaseDocument:
    doc = KnowledgeBaseDocument(**kwargs)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


async def delete_document(session: AsyncSession, doc: KnowledgeBaseDocument) -> None:
    await session.delete(doc)
    await session.commit()


async def get_call_logs_for_business(session: AsyncSession, business_id: uuid.UUID) -> Sequence[CallLog]:
    result = await session.execute(
        select(CallLog).where(CallLog.business_id == business_id).order_by(CallLog.created_at.desc())
    )
    return result.scalars().all()


async def create_call_log(session: AsyncSession, **kwargs: Any) -> CallLog:
    log = CallLog(**kwargs)
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log
