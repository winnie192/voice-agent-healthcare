from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BusinessCreate(BaseModel):
    name: str
    phone: str
    timezone: str = "UTC"
    location: str | None = None
    hours: dict | None = None
    policies: str | None = None
    admin_email: str
    admin_password: str


class BusinessUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    timezone: str | None = None
    location: str | None = None
    hours: dict | None = None
    policies: str | None = None


class BusinessResponse(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    timezone: str
    location: str | None
    hours: dict | None
    policies: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    duration_minutes: int
    price: float | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    price: float | None = None


class ServiceResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    description: str | None
    duration_minutes: int
    price: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingRuleUpdate(BaseModel):
    advance_notice_hours: int | None = None
    max_advance_days: int | None = None
    cancellation_hours: int | None = None
    allowed_days: list[str] | None = None


class BookingRuleResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    advance_notice_hours: int
    max_advance_days: int
    cancellation_hours: int
    allowed_days: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    service_id: uuid.UUID
    customer_name: str
    customer_phone: str
    start_time: datetime
    end_time: datetime
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    title: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CallLogResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    caller_phone: str | None
    transcript: str | None
    intent: str | None
    outcome: str | None
    duration_seconds: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
