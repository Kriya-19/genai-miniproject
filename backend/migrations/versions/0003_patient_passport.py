"""add patient passport profile fields

Revision ID: 0003_patient_passport
Revises: 0002_free_integrations
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_patient_passport"
down_revision = "0002_free_integrations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("sex", sa.String(length=30), nullable=True))
    op.add_column("users", sa.Column("allergies", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("users", sa.Column("conditions", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("users", sa.Column("medications", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("users", sa.Column("medical_history", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("users", "medical_history")
    op.drop_column("users", "medications")
    op.drop_column("users", "conditions")
    op.drop_column("users", "allergies")
    op.drop_column("users", "sex")
    op.drop_column("users", "age")
