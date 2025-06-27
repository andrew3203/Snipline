"""news_item

Revision ID: 7d74077081f9
Revises: None
Create Date: 2025-04-20 15:46:34.405542

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision = "7d74077081f9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("summary", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category", sa.Integer(), nullable=True),
        sa.Column(
            "subcategories", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("companies", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("locations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("names", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("lang", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_ready", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_item_id"), "news_item", ["id"], unique=False)
    op.create_index(
        "ix_news_item_companies",
        "news_item",
        ["companies"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        op.f("ix_news_item_locations"), "news_item", ["locations"], unique=False
    )
    op.create_index(
        op.f("ix_news_item_published_at"), "news_item", ["published_at"], unique=False
    )
    op.create_index(
        "ix_news_item_subcategories",
        "news_item",
        ["subcategories"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_news_item_id"), table_name="news_item")
    op.drop_index(
        "ix_news_item_subcategories", table_name="news_item", postgresql_using="gin"
    )
    op.drop_index(op.f("ix_news_item_published_at"), table_name="news_item")
    op.drop_index(op.f("ix_news_item_locations"), table_name="news_item")
    op.drop_index(
        "ix_news_item_companies", table_name="news_item", postgresql_using="gin"
    )
    op.drop_table("news_item")
