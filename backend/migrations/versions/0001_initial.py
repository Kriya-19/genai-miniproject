"""Create initial DiagnoSure tables."""
from alembic import op
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect
    bind = op.get_bind()
    tables = inspect(bind).get_table_names()
    if "users" not in tables:
        op.create_table(
            "users",
            Column("id", String(36), primary_key=True),
            Column("email", String(320), nullable=False, unique=True),
            Column("password_hash", String(255), nullable=False),
            Column("role", String(20), nullable=False),
            Column("full_name", String(200), nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)
    if "diagnosis_cases" not in tables:
        op.create_table(
            "diagnosis_cases",
            Column("id", String(36), primary_key=True),
            Column("user_id", String(36), nullable=True),
            Column("input_text", Text, nullable=False),
            Column("result_json", Text, nullable=True),
            Column("status", String(20), nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )
    if "health_records" not in tables:
        op.create_table(
            "health_records",
            Column("id", String(36), primary_key=True),
            Column("user_id", String(36), nullable=False),
            Column("category", String(40), nullable=False),
            Column("title", String(200), nullable=False),
            Column("details", Text, nullable=False),
            Column("file_path", String(500), nullable=True),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
    if "health_record_shares" not in tables:
        op.create_table(
            "health_record_shares",
            Column("id", String(36), primary_key=True),
            Column("owner_id", String(36), nullable=False),
            Column("doctor_id", String(36), nullable=False),
            Column("record_id", String(36), nullable=False),
            Column("expires_at", DateTime(timezone=True), nullable=False),
            Column("revoked", Boolean, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )
    if "consultations" not in tables:
        op.create_table(
            "consultations",
            Column("id", String(36), primary_key=True),
            Column("patient_id", String(36), nullable=False),
            Column("doctor_id", String(36), nullable=True),
            Column("scheduled_at", DateTime(timezone=True), nullable=False),
            Column("status", String(20), nullable=False),
            Column("notes", Text, nullable=False),
            Column("video_provider", String(30), nullable=False),
            Column("video_room", String(160), nullable=False, unique=True),
            Column("video_url", String(500), nullable=False),
        )
    if "reminders" not in tables:
        op.create_table(
            "reminders",
            Column("id", String(36), primary_key=True),
            Column("user_id", String(36), nullable=False),
            Column("title", String(200), nullable=False),
            Column("reminder_type", String(30), nullable=False),
            Column("scheduled_at", DateTime(timezone=True), nullable=False),
            Column("recurrence", String(30), nullable=True),
            Column("active", Boolean, nullable=False),
            Column("completed_at", DateTime(timezone=True), nullable=True),
        )
    if "reminder_events" not in tables:
        op.create_table(
            "reminder_events",
            Column("id", String(36), primary_key=True),
            Column("reminder_id", String(36), nullable=False),
            Column("scheduled_at", DateTime(timezone=True), nullable=False),
            Column("status", String(30), nullable=False),
            Column("message", Text, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )
    if "audit_logs" not in tables:
        op.create_table(
            "audit_logs",
            Column("id", Integer, primary_key=True),
            Column("user_id", String(36), nullable=True),
            Column("action", String(100), nullable=False),
            Column("resource_type", String(50), nullable=False),
            Column("resource_id", String(36), nullable=True),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )


def downgrade():
    for table in ("audit_logs", "reminder_events", "reminders", "consultations", "health_record_shares", "health_records", "diagnosis_cases", "users"):
        op.drop_table(table)
