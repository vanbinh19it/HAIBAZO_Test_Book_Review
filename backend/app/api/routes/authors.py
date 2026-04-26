from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
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
    skip = (page - 1) * page_size
    count_statement = select(func.count()).select_from(Author)
    count = session.exec(count_statement).one()
    statement = (
        select(Author)
        .order_by(col(Author.created_at).desc())
        .offset(skip)
        .limit(page_size)
    )
    authors = session.exec(statement).all()
    total = count
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    authors_public: list[AuthorPublic] = []
    for author in authors:
        books_count_statement = (
            select(func.count()).select_from(Book).where(Book.author_id == author.id)
        )
        books_count = session.exec(books_count_statement).one()
        authors_public.append(
            AuthorPublic(
                id=author.id,
                name=author.name,
                books_count=books_count,
                created_at=author.created_at,
            )
        )

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
    count_statement = select(func.count()).select_from(Book).where(Book.author_id == id)
    books_count = session.exec(count_statement).one()
    author_public = AuthorPublic(
        id=author.id,
        name=author.name,
        books_count=books_count,
        created_at=author.created_at,
    )
    return AuthorPublic.model_validate(author_public)


@router.post("/", response_model=AuthorPublic)
def create_author(
    *, session: SessionDep, _current_user: CurrentUser, author_in: AuthorCreate
) -> Any:
    """
    Create new author.
    """
    existing_author = session.exec(
        select(Author).where(Author.name == author_in.name)
    ).first()
    if existing_author:
        raise HTTPException(status_code=400, detail="Author already exists")

    author = Author.model_validate(author_in)
    session.add(author)
    session.commit()
    session.refresh(author)

    return AuthorPublic(
        id=author.id,
        name=author.name,
        books_count=0,
        created_at=author.created_at,
    )


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

    update_dict = author_in.model_dump(exclude_unset=True)
    if "name" in update_dict:
        existing_author = session.exec(
            select(Author).where(Author.name == update_dict["name"], Author.id != id)
        ).first()
        if existing_author:
            raise HTTPException(status_code=400, detail="Author already exists")

    author.sqlmodel_update(update_dict)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.delete("/{id}")
def delete_author(session: SessionDep, _current_user: CurrentUser, id: int) -> Message:
    """
    Delete an author.
    """
    author = session.get(Author, id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    session.delete(author)
    session.commit()
    return Message(message="Author deleted successfully")
