import uuid

from sqlmodel import Session

from app.models import Author
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_author(db: Session, owner_id: uuid.UUID | None = None) -> Author:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    assert owner_id is not None

    author = Author(name=f"author-{random_lower_string()}", owner_id=owner_id)
    db.add(author)
    db.commit()
    db.refresh(author)
    return author
