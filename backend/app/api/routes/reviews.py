from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, func, select

from app.api.authz import ensure_owner_or_superuser
from app.api.deps import CurrentUser, SessionDep
from app.api.pagination import get_pagination
from app.models import (
    Author,
    Book,
    Message,
    Review,
    ReviewCreate,
    ReviewPublic,
    ReviewsPublic,
    ReviewUpdate,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


def normalize_review_content(content: str) -> str:
    return content.strip()


def check_book_exists(session: SessionDep, book_id: int) -> Book:
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def to_review_public(
    review: Review, book_title: str | None, author_name: str | None
) -> ReviewPublic:
    return ReviewPublic(
        id=review.id,
        book_id=review.book_id,
        owner_id=review.owner_id,
        book_title=book_title,
        author_name=author_name,
        content=review.content,
        created_at=review.created_at,
    )


@router.get("/", response_model=ReviewsPublic)
def read_reviews(
    session: SessionDep,
    _current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> Any:
    """
    Retrieve reviews.
    """
    count_statement = select(func.count()).select_from(Review)
    if not _current_user.is_superuser:
        count_statement = count_statement.where(Review.owner_id == _current_user.id)
    count = session.exec(count_statement).one()
    skip, total_pages = get_pagination(page=page, page_size=page_size, total=count)
    statement = select(Review).order_by(col(Review.created_at).asc())
    if not _current_user.is_superuser:
        statement = statement.where(Review.owner_id == _current_user.id)
    statement = statement.offset(skip).limit(page_size)
    reviews = session.exec(statement).all()
    total = count

    books_by_id: dict[int, Book] = {}
    author_name_map: dict[int, str] = {}
    book_ids = list({review.book_id for review in reviews})

    if book_ids:
        books = session.exec(select(Book).where(col(Book.id).in_(book_ids))).all()
        books_by_id = {book.id: book for book in books}
        author_ids = list({book.author_id for book in books})
        if author_ids:
            authors = session.exec(
                select(Author).where(col(Author.id).in_(author_ids))
            ).all()
            author_name_map = {author.id: author.name for author in authors}

    reviews_public = []
    for review in reviews:
        book = books_by_id.get(review.book_id)
        book_title = book.title if book else None
        author_name = author_name_map.get(book.author_id) if book else None
        reviews_public.append(
            to_review_public(
                review=review,
                book_title=book_title,
                author_name=author_name,
            )
        )

    return ReviewsPublic(
        data=reviews_public,
        count=count,
        page=page,
        limit=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{id}", response_model=ReviewPublic)
def read_review(session: SessionDep, _current_user: CurrentUser, id: int) -> Any:
    """
    Get review by ID.
    """
    review = session.get(Review, id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    ensure_owner_or_superuser(
        current_user=_current_user,
        entity_owner_id=review.owner_id,
    )

    book = session.get(Book, review.book_id)
    author_name: str | None = None
    book_title: str | None = None

    if book:
        book_title = book.title
        author = session.get(Author, book.author_id)
        author_name = author.name if author else None

    return to_review_public(
        review=review,
        book_title=book_title,
        author_name=author_name,
    )


@router.post("/", response_model=ReviewPublic)
def create_review(
    *, session: SessionDep, _current_user: CurrentUser, review_in: ReviewCreate
) -> Any:
    """
    Create new review.
    """
    normalized_content = normalize_review_content(review_in.content)
    if not normalized_content:
        raise HTTPException(status_code=422, detail="Review is required")

    book = check_book_exists(session=session, book_id=review_in.book_id)
    ensure_owner_or_superuser(
        current_user=_current_user,
        entity_owner_id=book.owner_id,
    )
    author = session.get(Author, book.author_id)

    # Enforce ownership consistency with parent book.
    review = Review.model_validate(
        review_in, update={"owner_id": book.owner_id, "content": normalized_content}
    )
    session.add(review)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Invalid review data") from None
    session.refresh(review)
    return to_review_public(
        review=review,
        book_title=book.title,
        author_name=author.name if author else None,
    )


@router.put("/{id}", response_model=ReviewPublic)
def update_review(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    id: int,
    review_in: ReviewUpdate,
) -> Any:
    """
    Update a review.
    """
    review = session.get(Review, id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    ensure_owner_or_superuser(
        current_user=_current_user,
        entity_owner_id=review.owner_id,
    )

    update_dict = review_in.model_dump(exclude_unset=True)
    if "content" in update_dict:
        if update_dict["content"] is None:
            raise HTTPException(status_code=422, detail="Review is required")
        update_dict["content"] = normalize_review_content(update_dict["content"])
        if not update_dict["content"]:
            raise HTTPException(status_code=422, detail="Review is required")
    target_book_id = update_dict.get("book_id", review.book_id)
    book = check_book_exists(session=session, book_id=target_book_id)
    ensure_owner_or_superuser(
        current_user=_current_user,
        entity_owner_id=book.owner_id,
    )
    author = session.get(Author, book.author_id)

    review.sqlmodel_update(update_dict)
    # Keep owner aligned with parent book owner.
    review.owner_id = book.owner_id
    session.add(review)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Invalid review data") from None
    session.refresh(review)
    return to_review_public(
        review=review,
        book_title=book.title,
        author_name=author.name if author else None,
    )


@router.delete("/{id}")
def delete_review(session: SessionDep, _current_user: CurrentUser, id: int) -> Message:
    """
    Delete a review.
    """
    review = session.get(Review, id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    ensure_owner_or_superuser(
        current_user=_current_user,
        entity_owner_id=review.owner_id,
    )

    session.delete(review)
    session.commit()
    return Message(message="Review deleted successfully")
