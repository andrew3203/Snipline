"""subscription_plan

Revision ID: 8bc1c36d49f7
Revises: 026c9b686cf1
Create Date: 2025-04-20 15:55:39.551236

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8bc1c36d49f7"
down_revision = "026c9b686cf1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subscription_plan",
        sa.Column("id", sa.Integer(), nullable=False),
        # sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        # sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("price_usd", sa.Float(), nullable=False),
        sa.Column("days_duration", sa.Integer(), nullable=False),
        # sa.Column("features", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_subscription_plan_id"), "subscription_plan", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_subscription_plan_id"), table_name="subscription_plan")
    op.drop_table("subscription_plan")
