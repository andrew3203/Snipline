"""user_referral_reward

Revision ID: 13b3663745d7
Revises: d3baf5708596
Create Date: 2025-04-20 16:51:37.999303

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "13b3663745d7"
down_revision = "d3baf5708596"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_referral_reward",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reward_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["reward_id"],
            ["referral_reward.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_referral_reward")
