"""support

Revision ID: 9b9910425a27
Revises: 270523cc4b91
Create Date: 2025-04-20 17:02:03.249215

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "9b9910425a27"
down_revision = "270523cc4b91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "support",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("answer", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_support_user_id"), "support", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_support_user_id"), table_name="support")
    op.drop_table("support")
