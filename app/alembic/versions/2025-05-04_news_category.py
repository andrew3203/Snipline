"""news_category

Revision ID: acc37ef68e57
Revises: 8fe33b162f10
Create Date: 2025-05-04 10:36:30.894026

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "acc37ef68e57"
down_revision = "8fe33b162f10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news_category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_category_id"), "news_category", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_news_category_id"), table_name="news_category")
    op.drop_table("news_category")
