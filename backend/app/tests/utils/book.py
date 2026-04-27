import uuid

from sqlmodel import Session

from app.models import Author, Book
from app.tests.utils.author import create_random_author
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_book(
    db: Session,
    owner_id: uuid.UUID | None = None,
    author: Author | None = None,
) -> Book:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    assert owner_id is not None

    if author is None:
        author = create_random_author(db, owner_id=owner_id)

    book = Book(
        title=f"book-{random_lower_string()}",
        author_id=author.id,
        owner_id=owner_id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book
