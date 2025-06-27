"""dictionary

Revision ID: d6c07106b2e8
Revises: 9b9910425a27
Create Date: 2025-05-04 10:12:24.696537

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d6c07106b2e8"
down_revision = "9b9910425a27"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dictionary",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.TEXT()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dictionary_id"), "dictionary", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dictionary_id"), table_name="dictionary")
    op.drop_table("dictionary")
