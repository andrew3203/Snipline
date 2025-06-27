"""promo_offer_rule

Revision ID: 371c1ccce201
Revises: ff6ee01967a9
Create Date: 2025-04-20 16:48:02.865228

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "371c1ccce201"
down_revision = "ff6ee01967a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "promo_offer_rule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("discount_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("new_plan_id", sa.Integer(), nullable=False),
        sa.Column("minutes_duration", sa.Integer(), nullable=False),
        sa.Column("expire_days", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["discount_id"],
            ["discount.id"],
        ),
        sa.ForeignKeyConstraint(
            ["new_plan_id"],
            ["subscription_plan.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plan.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("promo_offer_rule")
