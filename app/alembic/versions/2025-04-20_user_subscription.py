"""user_subscription

Revision ID: 270523cc4b91
Revises: 327e7e4437cc
Create Date: 2025-04-20 17:01:02.077234

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "270523cc4b91"
down_revision = "327e7e4437cc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_subscription",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("promo_offer_id", sa.Integer(), nullable=True),
        sa.Column("payment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payment.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plan.id"],
        ),
        sa.ForeignKeyConstraint(
            ["promo_offer_id"],
            ["promo_offer.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_subscription")
