"""add detection_results_json column to image_upload

Revision ID: abcd1234efgh
Revises: 3008857b7d46
Create Date: 2025-07-20 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "abcd1234efgh"
down_revision = "3008857b7d46"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "image_upload",
        sa.Column(
            "detection_results_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("image_upload", "detection_results_json")
