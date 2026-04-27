"""add owner_id to author book review

Revision ID: f34ab12cd890
Revises: c12f9e4b7a21
Create Date: 2026-04-27 09:40:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "f34ab12cd890"
down_revision = "c12f9e4b7a21"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("author", sa.Column("owner_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_author_owner_id_user",
        "author",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("book", sa.Column("owner_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_book_owner_id_user",
        "book",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("review", sa.Column("owner_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_review_owner_id_user",
        "review",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("uq_author_name", "author", type_="unique")
    op.create_unique_constraint("uq_author_name_owner", "author", ["name", "owner_id"])

    op.drop_constraint("uq_book_title_author", "book", type_="unique")
    op.create_unique_constraint(
        "uq_book_title_author_owner", "book", ["title", "author_id", "owner_id"]
    )


def downgrade():
    op.drop_constraint("uq_book_title_author_owner", "book", type_="unique")
    op.create_unique_constraint("uq_book_title_author", "book", ["title", "author_id"])

    op.drop_constraint("uq_author_name_owner", "author", type_="unique")
    op.create_unique_constraint("uq_author_name", "author", ["name"])

    op.drop_constraint("fk_review_owner_id_user", "review", type_="foreignkey")
    op.drop_column("review", "owner_id")

    op.drop_constraint("fk_book_owner_id_user", "book", type_="foreignkey")
    op.drop_column("book", "owner_id")

    op.drop_constraint("fk_author_owner_id_user", "author", type_="foreignkey")
    op.drop_column("author", "owner_id")
