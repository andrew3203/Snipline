"""promo_offer

Revision ID: 327e7e4437cc
Revises: cf81ec639736
Create Date: 2025-04-20 17:00:00.613603

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "327e7e4437cc"
down_revision = "cf81ec639736"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "promo_offer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("discount_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["discount_id"],
            ["discount.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plan.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("promo_offer")
