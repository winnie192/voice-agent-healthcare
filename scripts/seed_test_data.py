"""Seed script: creates a test healthcare clinic with services, booking rules,
and knowledge base documents (ingested into ChromaDB).

Usage:
    python3 -m scripts.seed_test_data
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.engine import async_session_factory
from src.api.db.queries import (
    create_admin_user,
    create_business,
    create_document,
    create_service,
    upsert_booking_rules,
)
from passlib.context import CryptContext

from src.api.rag.ingest import ingest_document

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


BUSINESS_CONFIG = {
    "name": "HealthFirst Medical Clinic",
    "phone": "+14155550100",
    "timezone": "America/Los_Angeles",
    "location": "456 Wellness Ave, San Francisco, CA 94102",
    "hours": {
        "monday": "8:00-18:00",
        "tuesday": "8:00-18:00",
        "wednesday": "8:00-18:00",
        "thursday": "8:00-18:00",
        "friday": "8:00-17:00",
        "saturday": "9:00-13:00",
        "sunday": "closed",
    },
    "policies": (
        "Cancellations must be made at least 24 hours in advance. "
        "A $25 no-show fee applies. Insurance accepted: Aetna, Blue Cross, Cigna, United. "
        "New patients should arrive 15 minutes early to complete paperwork."
    ),
}

ADMIN_USER = {
    "email": "admin@healthfirst.test",
    "password": "testpass123",
}

SERVICES = [
    {
        "name": "General Consultation",
        "description": "Routine check-up or new concern with a general practitioner.",
        "duration_minutes": 30,
        "price": 150.00,
    },
    {
        "name": "Dental Cleaning",
        "description": "Standard dental cleaning and oral examination.",
        "duration_minutes": 45,
        "price": 120.00,
    },
    {
        "name": "Physical Therapy Session",
        "description": "One-on-one session with a licensed physical therapist.",
        "duration_minutes": 60,
        "price": 200.00,
    },
    {
        "name": "Eye Exam",
        "description": "Comprehensive vision and eye health examination.",
        "duration_minutes": 30,
        "price": 100.00,
    },
]

BOOKING_RULES = {
    "advance_notice_hours": 24,
    "max_advance_days": 60,
    "cancellation_hours": 24,
    "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
}

KB_DOCUMENTS = [
    {
        "title": "Clinic Overview & Services",
        "content": (
            "HealthFirst Medical Clinic is a full-service healthcare facility located at "
            "456 Wellness Ave, San Francisco. We have been serving the Bay Area since 2015.\n\n"
            "Our services include:\n"
            "- General Consultation ($150, 30 min): Meet with one of our board-certified "
            "general practitioners for routine check-ups, sick visits, or new health concerns.\n"
            "- Dental Cleaning ($120, 45 min): Professional cleaning by our hygienists, "
            "including plaque removal, polishing, and an oral exam by the dentist.\n"
            "- Physical Therapy ($200, 60 min): Individualized rehab sessions for injury "
            "recovery, chronic pain management, and mobility improvement.\n"
            "- Eye Exam ($100, 30 min): Complete vision screening and eye health assessment "
            "using the latest diagnostic equipment.\n\n"
            "We accept most major insurance plans including Aetna, Blue Cross Blue Shield, "
            "Cigna, and United Healthcare. Self-pay patients receive a 10% discount."
        ),
    },
    {
        "title": "Appointment & Cancellation Policy",
        "content": (
            "Booking Policy:\n"
            "- Appointments must be booked at least 24 hours in advance.\n"
            "- You can schedule up to 60 days ahead.\n"
            "- Same-day appointments may be available for urgent needs; please call to check.\n\n"
            "Cancellation Policy:\n"
            "- Cancellations must be made at least 24 hours before the appointment.\n"
            "- Late cancellations (less than 24 hours) incur a $25 fee.\n"
            "- No-shows are charged the full consultation fee.\n"
            "- To cancel, call us at +1 (415) 555-0100 or use the online portal.\n\n"
            "Rescheduling:\n"
            "- You may reschedule free of charge if done 24+ hours in advance.\n"
            "- Rescheduled appointments are subject to availability."
        ),
    },
    {
        "title": "Insurance & Billing",
        "content": (
            "Accepted Insurance Plans:\n"
            "- Aetna (PPO and HMO)\n"
            "- Blue Cross Blue Shield\n"
            "- Cigna\n"
            "- United Healthcare\n"
            "- Medicare (Parts A and B)\n\n"
            "Billing Information:\n"
            "- Co-pays are collected at the time of the visit.\n"
            "- We will file claims with your insurance on your behalf.\n"
            "- For uninsured patients, we offer a 10% self-pay discount.\n"
            "- Payment plans are available for balances over $500.\n"
            "- We accept cash, credit/debit cards, and HSA/FSA cards."
        ),
    },
    {
        "title": "Doctors & Staff",
        "content": (
            "Our Team:\n\n"
            "Dr. Sarah Chen, MD - General Practitioner\n"
            "Board-certified in Family Medicine with 12 years of experience. "
            "Specializes in preventive care and chronic disease management.\n\n"
            "Dr. James Rodriguez, DDS - Dentist\n"
            "Graduate of UCSF School of Dentistry. Offers general and cosmetic dentistry.\n\n"
            "Maria Thompson, DPT - Physical Therapist\n"
            "Licensed physical therapist specializing in sports injuries and post-surgical rehab. "
            "15 years of clinical experience.\n\n"
            "Dr. Priya Patel, OD - Optometrist\n"
            "Comprehensive eye care including contact lens fittings and management of eye diseases."
        ),
    },
    {
        "title": "Location & Hours",
        "content": (
            "Address: 456 Wellness Ave, San Francisco, CA 94102\n"
            "Phone: +1 (415) 555-0100\n"
            "Email: info@healthfirst.test\n\n"
            "Hours of Operation:\n"
            "Monday - Thursday: 8:00 AM - 6:00 PM\n"
            "Friday: 8:00 AM - 5:00 PM\n"
            "Saturday: 9:00 AM - 1:00 PM\n"
            "Sunday: Closed\n\n"
            "Parking: Free parking is available in the building garage. "
            "Enter from Oak Street.\n\n"
            "Public Transit: We are a 5-minute walk from the Civic Center BART station."
        ),
    },
]


async def seed(session: AsyncSession) -> uuid.UUID:
    business = await create_business(session, **BUSINESS_CONFIG)
    biz_id = business.id
    print(f"Created business: {business.name} (id={biz_id})")

    await create_admin_user(
        session,
        business_id=biz_id,
        email=ADMIN_USER["email"],
        hashed_password=pwd_context.hash(ADMIN_USER["password"]),
    )
    print(f"Created admin user: {ADMIN_USER['email']}")

    for svc in SERVICES:
        s = await create_service(session, business_id=biz_id, **svc)
        print(f"  Service: {s.name}")

    await upsert_booking_rules(session, biz_id, **BOOKING_RULES)
    print("  Booking rules configured")

    for doc_data in KB_DOCUMENTS:
        doc = await create_document(
            session,
            business_id=biz_id,
            title=doc_data["title"],
            content=doc_data["content"],
        )
        print(f"  KB doc: {doc.title}")
        try:
            col_name = await ingest_document(biz_id, doc.id, doc.content, doc.title)
            print(f"    -> ingested to ChromaDB collection: {col_name}")
        except Exception as e:
            print(f"    -> ChromaDB ingest failed (is ChromaDB running?): {e}")

    await session.commit()
    print(f"\nDone! Login with: {ADMIN_USER['email']} / {ADMIN_USER['password']}")
    return biz_id


async def main() -> None:
    async with async_session_factory() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
