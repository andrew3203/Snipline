"""data_dictionary

Revision ID: 8fe33b162f10
Revises: d6c07106b2e8
Create Date: 2025-05-04 10:20:46.694767

"""

import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "8fe33b162f10"
down_revision = "d6c07106b2e8"
branch_labels = None
depends_on = None


def load_categories():
    with open("alembic/data/dictionary.json", encoding="utf-8") as f:
        return json.load(f)


def upgrade() -> None:
    raw_data = load_categories()
    dictionary_table = sa.table(
        "dictionary", sa.column("id", sa.String), sa.column("data", postgresql.JSONB)
    )
    op.bulk_insert(dictionary_table, raw_data)


def downgrade() -> None:
    keys = [item["key"] for item in load_categories()]
    keys_str = ", ".join(f"'{k}'" for k in keys)
    op.execute(f"DELETE FROM dictionary WHERE key IN ({keys_str})")
