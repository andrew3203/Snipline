"""news_report

Revision ID: 2e025b681772
Revises: 13b3663745d7
Create Date: 2025-04-20 16:53:05.966547

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision = "2e025b681772"
down_revision = "13b3663745d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news_report",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("lang", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("news_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("filter_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reaction", sa.Integer(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["filter_id"],
            ["user_filter.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_news_report_filter_id"), "news_report", ["filter_id"], unique=False
    )
    op.create_index(
        op.f("ix_news_report_user_id"), "news_report", ["user_id"], unique=False
    )
    op.create_index(op.f("ix_news_report_lang"), "news_report", ["lang"], unique=False)
    op.create_index(op.f("ix_news_report_id"), "news_report", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_news_report_id"), table_name="news_report")
    op.drop_index(op.f("ix_news_lang"), table_name="news_report")
    op.drop_index(op.f("ix_news_report_user_id"), table_name="news_report")
    op.drop_index(op.f("ix_news_report_filter_id"), table_name="news_report")
    op.drop_table("news_report")
