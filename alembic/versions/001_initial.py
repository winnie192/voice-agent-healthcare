"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-01-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "businesses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("timezone", sa.String(50), server_default="UTC"),
        sa.Column("location", sa.Text, nullable=True),
        sa.Column("hours", JSONB, nullable=True),
        sa.Column("policies", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "admin_users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "knowledge_base_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("chroma_collection", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "services",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "booking_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("advance_notice_hours", sa.Integer, server_default="24"),
        sa.Column("max_advance_days", sa.Integer, server_default="30"),
        sa.Column("cancellation_hours", sa.Integer, server_default="24"),
        sa.Column("allowed_days", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "bookings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_id", UUID(as_uuid=True), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("customer_phone", sa.String(20), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="confirmed"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "call_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("caller_phone", sa.String(20), nullable=True),
        sa.Column("transcript", sa.Text, nullable=True),
        sa.Column("intent", sa.String(100), nullable=True),
        sa.Column("outcome", sa.String(100), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("call_logs")
    op.drop_table("bookings")
    op.drop_table("booking_rules")
    op.drop_table("services")
    op.drop_table("knowledge_base_documents")
    op.drop_table("admin_users")
    op.drop_table("businesses")
