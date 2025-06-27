"""discount

Revision ID: 1c4d6e0e9dc5
Revises: 7d74077081f9
Create Date: 2025-04-20 15:51:46.520939

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "1c4d6e0e9dc5"
down_revision = "7d74077081f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "discount",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_discount_id"), "discount", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_discount_id"), table_name="discount")
    op.drop_table("discount")
