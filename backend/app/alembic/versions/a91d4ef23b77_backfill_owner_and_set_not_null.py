"""backfill owner and set not null

Revision ID: a91d4ef23b77
Revises: f34ab12cd890
Create Date: 2026-04-27 10:25:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "a91d4ef23b77"
down_revision = "f34ab12cd890"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    fallback_owner_id = bind.execute(
        sa.text(
            """
            SELECT id FROM "user"
            WHERE is_superuser = true
            ORDER BY created_at LIMIT 1
            """
        )
    ).scalar_one_or_none()

    has_legacy_rows = bind.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM author
                UNION ALL
                SELECT 1 FROM book
                UNION ALL
                SELECT 1 FROM review
            )
            """
        )
    ).scalar()
    if has_legacy_rows and fallback_owner_id is None:
        raise RuntimeError(
            "Cannot backfill owner_id: existing data found but no superuser was found. "
            "Please create a superuser before running migrations."
        )

    if fallback_owner_id is not None:
        bind.execute(
            sa.text(
                """
                UPDATE author
                SET owner_id = :fallback_owner_id
                WHERE owner_id IS NULL
                """
            ),
            {"fallback_owner_id": fallback_owner_id},
        )

    bind.execute(
        sa.text(
            """
            UPDATE book
            SET owner_id = author.owner_id
            FROM author
            WHERE book.author_id = author.id
              AND book.owner_id IS NULL
            """
        )
    )
    if fallback_owner_id is not None:
        bind.execute(
            sa.text(
                """
                UPDATE book
                SET owner_id = :fallback_owner_id
                WHERE owner_id IS NULL
                """
            ),
            {"fallback_owner_id": fallback_owner_id},
        )

    bind.execute(
        sa.text(
            """
            UPDATE review
            SET owner_id = book.owner_id
            FROM book
            WHERE review.book_id = book.id
              AND review.owner_id IS NULL
            """
        )
    )
    if fallback_owner_id is not None:
        bind.execute(
            sa.text(
                """
                UPDATE review
                SET owner_id = :fallback_owner_id
                WHERE owner_id IS NULL
                """
            ),
            {"fallback_owner_id": fallback_owner_id},
        )

    op.alter_column("author", "owner_id", existing_type=sa.Uuid(), nullable=False)
    op.alter_column("book", "owner_id", existing_type=sa.Uuid(), nullable=False)
    op.alter_column("review", "owner_id", existing_type=sa.Uuid(), nullable=False)


def downgrade():
    op.alter_column("review", "owner_id", existing_type=sa.Uuid(), nullable=True)
    op.alter_column("book", "owner_id", existing_type=sa.Uuid(), nullable=True)
    op.alter_column("author", "owner_id", existing_type=sa.Uuid(), nullable=True)
