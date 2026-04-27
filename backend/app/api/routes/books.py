from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.api.pagination import get_pagination
from app.models import (
    Author,
    Book,
    BookCreate,
    BookPublic,
    BooksPublic,
    BookUpdate,
    Message,
)

router = APIRouter(prefix="/books", tags=["books"])


def check_author_exists(session: SessionDep, author_id: int) -> Author | None:
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


def to_book_public(book: Book, author_name: str | None) -> BookPublic:
    return BookPublic(
        id=book.id,
        title=book.title,
        author_id=book.author_id,
        owner_id=book.owner_id,
        author_name=author_name,
        created_at=book.created_at,
    )


@router.get("/", response_model=BooksPublic)
def read_books(
    session: SessionDep,
    _current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> Any:
    """
    Retrieve books.
    """
    count_statement = select(func.count()).select_from(Book)
    if not _current_user.is_superuser:
        count_statement = count_statement.where(Book.owner_id == _current_user.id)
    count = session.exec(count_statement).one()
    skip, total_pages = get_pagination(page=page, page_size=page_size, total=count)
    statement = select(Book).order_by(col(Book.created_at).desc())
    if not _current_user.is_superuser:
        statement = statement.where(Book.owner_id == _current_user.id)
    statement = statement.offset(skip).limit(page_size)
    books = session.exec(statement).all()
    total = count

    author_name_map: dict[int, str] = {}
    author_ids = list({book.author_id for book in books})
    if author_ids:
        authors = session.exec(select(Author).where(col(Author.id).in_(author_ids))).all()
        author_name_map = {author.id: author.name for author in authors}

    books_public = [
        to_book_public(book=book, author_name=author_name_map.get(book.author_id))
        for book in books
    ]

    return BooksPublic(
        data=books_public,
        count=count,
        page=page,
        limit=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{id}", response_model=BookPublic)
def read_book(session: SessionDep, _current_user: CurrentUser, id: int) -> Any:
    """
    Get book by ID.
    """
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not _current_user.is_superuser and (book.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    author = session.get(Author, book.author_id)
    return to_book_public(book=book, author_name=author.name if author else None)


@router.post("/", response_model=BookPublic)
def create_book(
    *, session: SessionDep, _current_user: CurrentUser, book_in: BookCreate
) -> Any:
    """
    Create new book.
    """
    author = check_author_exists(session=session, author_id=book_in.author_id)
    if not _current_user.is_superuser and (author.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    existing_book_statement = select(Book).where(
        Book.title == book_in.title,
        Book.author_id == book_in.author_id,
    )
    if not _current_user.is_superuser:
        existing_book_statement = existing_book_statement.where(
            Book.owner_id == _current_user.id
        )
    existing_book = session.exec(existing_book_statement).first()
    if existing_book:
        raise HTTPException(
            status_code=400, detail="Book already exists for this author"
        )

    book = Book.model_validate(book_in, update={"owner_id": _current_user.id})
    session.add(book)
    session.commit()
    session.refresh(book)
    return to_book_public(book=book, author_name=author.name)


@router.put("/{id}", response_model=BookPublic)
def update_book(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    id: int,
    book_in: BookUpdate,
) -> Any:
    """
    Update a book.
    """
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not _current_user.is_superuser and (book.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = book_in.model_dump(exclude_unset=True)
    target_author_id = update_dict.get("author_id", book.author_id)
    target_title = update_dict.get("title", book.title)

    author = check_author_exists(session=session, author_id=target_author_id)
    if not _current_user.is_superuser and (author.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    existing_book_statement = select(Book).where(
        Book.title == target_title,
        Book.author_id == target_author_id,
        Book.id != id,
    )
    if not _current_user.is_superuser:
        existing_book_statement = existing_book_statement.where(
            Book.owner_id == _current_user.id
        )
    existing_book = session.exec(existing_book_statement).first()
    if existing_book:
        raise HTTPException(
            status_code=400, detail="Book already exists for this author"
        )

    book.sqlmodel_update(update_dict)
    session.add(book)
    session.commit()
    session.refresh(book)
    return to_book_public(book=book, author_name=author.name)


@router.delete("/{id}")
def delete_book(session: SessionDep, _current_user: CurrentUser, id: int) -> Message:
    """
    Delete a book.
    """
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not _current_user.is_superuser and (book.owner_id != _current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(book)
    session.commit()
    return Message(message="Book deleted successfully")
