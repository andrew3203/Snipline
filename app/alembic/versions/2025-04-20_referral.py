"""referral

Revision ID: 2a4188bb328f
Revises: 371c1ccce201
Create Date: 2025-04-20 16:49:13.086424

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "2a4188bb328f"
down_revision = "371c1ccce201"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "referral",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("referrer_id", sa.Integer(), nullable=True),
        sa.Column("referred_id", sa.Integer(), nullable=True),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_paid", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["referred_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["referrer_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_referral_referred_id"), "referral", ["referred_id"], unique=False
    )
    op.create_index(
        op.f("ix_referral_referrer_id"), "referral", ["referrer_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_referral_referrer_id"), table_name="referral")
    op.drop_index(op.f("ix_referral_referred_id"), table_name="referral")
    op.drop_table("referral")
