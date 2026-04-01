"""add flag choice value

Revision ID: 8d3c1a2f4e5a
Revises: 1ee5b63e716f
Create Date: 2024-05-24 10:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.expression import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "8d3c1a2f4e5a"
down_revision = "1ee5b63e716f"
branch_labels = None
depends_on = None

try:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
except:
    conn = None
    inspector = None
    tables = None


def _table_has_column(table, column):
    if not inspector:
        return True
    has_column = False
    for col in inspector.get_columns(table):
        if column not in col["name"]:
            continue
        has_column = True
    return has_column


def upgrade():
    if not _table_has_column("flag_choice", "_value"):
        op.add_column("flag_choice", sa.Column("_value", sa.INTEGER))


def downgrade():
    if _table_has_column("flag_choice", "_value"):
        op.drop_column("flag_choice", "_value")
