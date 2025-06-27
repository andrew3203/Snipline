"""user_filter

Revision ID: d37b322f859f
Revises: 8fec8d09033c
Create Date: 2025-04-20 16:43:58.553255

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision = "d37b322f859f"
down_revision = "8fec8d09033c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_filter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_filter_id"), "user_filter", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_filter_user_id"), "user_filter", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_filter_user_id"), table_name="user_filter")
    op.drop_index(op.f("ix_user_filter_id"), table_name="user_filter")
    op.drop_table("user_filter")
