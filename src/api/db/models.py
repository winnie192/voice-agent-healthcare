import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

JSONB = JSON


class Base(DeclarativeBase):
    pass


def gen_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    hours: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    policies: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    admin_users: Mapped[list["AdminUser"]] = relationship(back_populates="business")
    documents: Mapped[list["KnowledgeBaseDocument"]] = relationship(back_populates="business")
    services: Mapped[list["Service"]] = relationship(back_populates="business")
    booking_rules: Mapped[list["BookingRule"]] = relationship(back_populates="business")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="business")
    call_logs: Mapped[list["CallLog"]] = relationship(back_populates="business")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="admin_users")


class KnowledgeBaseDocument(Base):
    __tablename__ = "knowledge_base_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    chroma_collection: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="documents")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int]
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="services")


class BookingRule(Base):
    __tablename__ = "booking_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), unique=True)
    advance_notice_hours: Mapped[int] = mapped_column(default=24)
    max_advance_days: Mapped[int] = mapped_column(default=30)
    cancellation_hours: Mapped[int] = mapped_column(default=24)
    allowed_days: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="booking_rules")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    customer_name: Mapped[str] = mapped_column(String(255))
    customer_phone: Mapped[str] = mapped_column(String(20))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="bookings")
    service: Mapped["Service"] = relationship()


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    caller_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="call_logs")
