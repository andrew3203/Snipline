"""payment

Revision ID: ff6ee01967a9
Revises: d37b322f859f
Create Date: 2025-04-20 16:45:20.830055

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "ff6ee01967a9"
down_revision = "d37b322f859f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount_usd", sa.Float(), nullable=False),
        sa.Column("method_id", sa.Integer(), nullable=False),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["method_id"],
            ["payment_method.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_id"), "payment", ["id"], unique=False)
    op.create_index(
        op.f("ix_payment_method_id"), "payment", ["method_id"], unique=False
    )
    op.create_index(op.f("ix_payment_user_id"), "payment", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_user_id"), table_name="payment")
    op.drop_index(op.f("ix_payment_method_id"), table_name="payment")
    op.drop_index(op.f("ix_payment_id"), table_name="payment")
    op.drop_table("payment")
