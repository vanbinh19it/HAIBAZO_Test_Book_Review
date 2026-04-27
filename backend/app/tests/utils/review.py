import uuid

from sqlmodel import Session

from app.models import Book, Review
from app.tests.utils.book import create_random_book
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_review(
    db: Session,
    owner_id: uuid.UUID | None = None,
    book: Book | None = None,
) -> Review:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    assert owner_id is not None

    if book is None:
        book = create_random_book(db, owner_id=owner_id)

    review = Review(
        content=f"review-{random_lower_string()}",
        book_id=book.id,
        owner_id=owner_id,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
