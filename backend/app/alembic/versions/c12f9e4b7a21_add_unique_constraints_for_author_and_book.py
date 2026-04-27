"""add unique constraints for author and book

Revision ID: c12f9e4b7a21
Revises: ea497dfc1b08
Create Date: 2026-04-26 23:20:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "c12f9e4b7a21"
down_revision = "ea497dfc1b08"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_author_name", "author", ["name"])
    op.create_unique_constraint("uq_book_title_author", "book", ["title", "author_id"])


def downgrade():
    op.drop_constraint("uq_book_title_author", "book", type_="unique")
    op.drop_constraint("uq_author_name", "author", type_="unique")
