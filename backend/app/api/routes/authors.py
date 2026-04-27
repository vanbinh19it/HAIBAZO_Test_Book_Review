from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.api.pagination import get_pagination
from app.models import (
    Author,
    AuthorCreate,
    AuthorPublic,
    AuthorsPublic,
    AuthorUpdate,
    Message,
    Book,
)

router = APIRouter(prefix="/authors", tags=["authors"])


def to_author_public(author: Author, books_count: int) -> AuthorPublic:
    return AuthorPublic(
        id=author.id,
        name=author.name,
        owner_id=author.owner_id,
        books_count=books_count,
        created_at=author.created_at,
    )


@router.get("/", response_model=AuthorsPublic)
def read_authors(
    session: SessionDep,
    _current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> Any:
    """
    Retrieve authors.
    """
    count_statement = select(func.count()).select_from(Author)
    if not _current_user.is_superuser:
        count_statement = count_statement.where(Author.owner_id == _current_user.id)
    count = session.exec(count_statement).one()
    skip, total_pages = get_pagination(page=page, page_size=page_size, total=count)
    statement = select(Author).order_by(col(Author.created_at).desc())
    if not _current_user.is_superuser:
        statement = statement.where(Author.owner_id == _current_user.id)
    statement = statement.offset(skip).limit(page_size)
    authors = session.exec(statement).all()
    total = count

    books_count_map: dict[int, int] = {}
    author_ids = [author.id for author in authors]
    if author_ids:
        books_count_rows = session.exec(
            select(Book.author_id, func.count())
            .where(col(Book.author_id).in_(author_ids))
            .group_by(Book.author_id)
        ).all()
        books_count_map = {author_id: book_count for author_id, book_count in books_count_rows}

    authors_public = [
        to_author_public(author=author, books_count=books_count_map.get(author.id, 0))
        for author in authors
    ]

    return AuthorsPublic(
        data=authors_public,
        count=count,
        page=page,
        limit=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{id}", response_model=AuthorPublic)
def read_author(session: SessionDep, _current_user: CurrentUser, id: int) -> Any:
    """
    Get author by ID.
    """
    author = session.get(Author, id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not _current_user.is_superuser and (author.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    count_statement = select(func.count()).select_from(Book).where(Book.author_id == id)
    books_count = session.exec(count_statement).one()
    return to_author_public(author=author, books_count=books_count)


@router.post("/", response_model=AuthorPublic)
def create_author(
    *, session: SessionDep, _current_user: CurrentUser, author_in: AuthorCreate
) -> Any:
    """
    Create new author.
    """
    existing_author_statement = select(Author).where(Author.name == author_in.name)
    if not _current_user.is_superuser:
        existing_author_statement = existing_author_statement.where(
            Author.owner_id == _current_user.id
        )
    existing_author = session.exec(existing_author_statement).first()
    if existing_author:
        raise HTTPException(status_code=400, detail="Author already exists")

    author = Author.model_validate(author_in, update={"owner_id": _current_user.id})
    session.add(author)
    session.commit()
    session.refresh(author)

    return to_author_public(author=author, books_count=0)


@router.put("/{id}", response_model=AuthorPublic)
def update_author(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    id: int,
    author_in: AuthorUpdate,
) -> Any:
    """
    Update an author.
    """
    author = session.get(Author, id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not _current_user.is_superuser and (author.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = author_in.model_dump(exclude_unset=True)
    if "name" in update_dict:
        existing_author_statement = select(Author).where(
            Author.name == update_dict["name"], Author.id != id
        )
        if not _current_user.is_superuser:
            existing_author_statement = existing_author_statement.where(
                Author.owner_id == _current_user.id
            )
        existing_author = session.exec(existing_author_statement).first()
        if existing_author:
            raise HTTPException(status_code=400, detail="Author already exists")

    author.sqlmodel_update(update_dict)
    session.add(author)
    session.commit()
    session.refresh(author)
    books_count_statement = select(func.count()).select_from(Book).where(Book.author_id == id)
    books_count = session.exec(books_count_statement).one()
    return to_author_public(author=author, books_count=books_count)


@router.delete("/{id}")
def delete_author(session: SessionDep, _current_user: CurrentUser, id: int) -> Message:
    """
    Delete an author.
    """
    author = session.get(Author, id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not _current_user.is_superuser and (author.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(author)
    session.commit()
    return Message(message="Author deleted successfully")
