"""Add provider fields and reminder event persistence."""
from alembic import op
import sqlalchemy as sa

revision = "0002_free_integrations"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    consultation_columns = {column["name"] for column in inspector.get_columns("consultations")}
    if "video_provider" not in consultation_columns:
        op.add_column("consultations", sa.Column("video_provider", sa.String(30), nullable=True))
        op.add_column("consultations", sa.Column("video_room", sa.String(160), nullable=True))
        op.add_column("consultations", sa.Column("video_url", sa.String(500), nullable=True))
        op.execute(
            "UPDATE consultations SET video_provider = 'jitsi', "
            "video_room = 'legacy-' || id, "
            "video_url = 'https://meet.jit.si/legacy-' || id"
        )
        with op.batch_alter_table("consultations") as batch:
            batch.alter_column("video_provider", nullable=False)
            batch.alter_column("video_room", nullable=False)
            batch.alter_column("video_url", nullable=False)
            batch.create_unique_constraint("uq_consultations_video_room", ["video_room"])

    if "reminder_events" not in inspector.get_table_names():
        op.create_table(
            "reminder_events",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("reminder_id", sa.String(36), nullable=False),
            sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("message", sa.Text, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade():
    op.drop_table("reminder_events")
    with op.batch_alter_table("consultations") as batch:
        batch.drop_constraint("uq_consultations_video_room", type_="unique")
        batch.drop_column("video_url")
        batch.drop_column("video_room")
        batch.drop_column("video_provider")
