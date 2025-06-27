"""payment_method

Revision ID: 026c9b686cf1
Revises: 1c4d6e0e9dc5
Create Date: 2025-04-20 15:53:40.527287

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "026c9b686cf1"
down_revision = "1c4d6e0e9dc5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_method",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_payment_method_type"), "payment_method", ["type"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_method_type"), table_name="payment_method")
    op.drop_table("payment_method")
