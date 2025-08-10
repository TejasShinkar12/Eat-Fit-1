"""merge heads

Revision ID: 6f4530195f9e
Revises: abcd1234efgh, 7f1571062140
Create Date: 2025-08-09 13:06:10.423857

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f4530195f9e"
down_revision: Union[str, None] = ("abcd1234efgh", "7f1571062140")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
