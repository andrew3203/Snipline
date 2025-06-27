"""referral_reward

Revision ID: d3baf5708596
Revises: 2a4188bb328f
Create Date: 2025-04-20 16:50:42.171072

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d3baf5708596"
down_revision = "2a4188bb328f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "referral_reward",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("referal_count", sa.Integer(), nullable=False),
        sa.Column("reward_plan_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["reward_plan_id"],
            ["subscription_plan.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("referral_reward")
