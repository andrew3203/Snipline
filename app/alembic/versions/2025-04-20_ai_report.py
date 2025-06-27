"""ai_report

Revision ID: cf81ec639736
Revises: 2e025b681772
Create Date: 2025-04-20 16:55:14.444661

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "cf81ec639736"
down_revision = "2e025b681772"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_report",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=True),
        sa.Column("question", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("answer", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("reaction", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["news_report.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_report_id"), "ai_report", ["id"], unique=False)
    op.create_index(
        op.f("ix_ai_report_user_id"), "ai_report", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_report_user_id"), table_name="ai_report")
    op.drop_index(op.f("ix_ai_report_id"), table_name="ai_report")
    op.drop_table("ai_report")
