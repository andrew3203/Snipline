"""news_category

Revision ID: d2c4d2c2b131
Revises: acc37ef68e57
Create Date: 2025-05-10 15:34:41.302454

"""

import json
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d2c4d2c2b131"
down_revision = "acc37ef68e57"
branch_labels = None
depends_on = None


def load_categories():
    with open("alembic/data/categories.json", encoding="utf-8") as f:
        return json.load(f)


def upgrade() -> None:
    raw_data = load_categories()
    dictionary_table = sa.table(
        "news_category",
        sa.column("id", sa.Integer),
        sa.column("parent_id", sa.Integer),
    )
    op.bulk_insert(dictionary_table, raw_data)


def downgrade() -> None:
    keys = [item["id"] for item in load_categories()]
    keys_str = ", ".join(f"'{k}'" for k in keys)
    op.execute(f"DELETE FROM news_category WHERE id IN ({keys_str})")
