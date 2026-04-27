from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.author import create_random_author
from app.tests.utils.book import create_random_book
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import random_email, random_lower_string


def _get_current_user_id(client: TestClient, headers: dict[str, str]) -> str:
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_create_book(client: TestClient, normal_user_token_headers: dict[str, str], db: Session) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    author = create_random_author(db, owner_id=current_user_id)
    data = {"title": f"book-{random_lower_string()}", "author_id": author.id}
    response = client.post(
        f"{settings.API_V1_STR}/books/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["author_id"] == author.id
    assert content["author_name"] == author.name
    assert content["owner_id"] == current_user_id


def test_create_book_duplicate_same_owner(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    author = create_random_author(db, owner_id=current_user_id)
    data = {"title": f"book-{random_lower_string()}", "author_id": author.id}
    first = client.post(
        f"{settings.API_V1_STR}/books/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert first.status_code == 200

    second = client.post(
        f"{settings.API_V1_STR}/books/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert second.status_code == 400
    assert second.json()["detail"] == "Book already exists for this author"


def test_create_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    other_author = create_random_author(db, owner_id=other_owner_id)
    data = {"title": f"book-{random_lower_string()}", "author_id": other_author.id}
    response = client.post(
        f"{settings.API_V1_STR}/books/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_book(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    book = create_random_book(db, owner_id=current_user_id)
    response = client.get(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == book.id
    assert content["title"] == book.title
    assert content["author_id"] == book.author_id
    assert content["owner_id"] == current_user_id


def test_read_book_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/books/999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_read_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    book = create_random_book(db, owner_id=other_owner_id)
    response = client.get(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_books_scoped_for_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    own_book = create_random_book(db, owner_id=current_user_id)
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    create_random_book(db, owner_id=other_owner_id)

    response = client.get(
        f"{settings.API_V1_STR}/books/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    book_ids = {item["id"] for item in content["data"]}
    assert own_book.id in book_ids
    for item in content["data"]:
        assert item["owner_id"] == current_user_id


def test_update_book(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    author = create_random_author(db, owner_id=current_user_id)
    book = create_random_book(db, owner_id=current_user_id, author=author)
    data = {"title": f"updated-{random_lower_string()}"}
    response = client.put(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == book.id
    assert content["title"] == data["title"]
    assert content["owner_id"] == current_user_id


def test_update_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    book = create_random_book(db, owner_id=other_owner_id)
    data = {"title": f"updated-{random_lower_string()}"}
    response = client.put(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_delete_book(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    book = create_random_book(db, owner_id=current_user_id)
    response = client.delete(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Book deleted successfully"


def test_delete_book_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    book = create_random_book(db, owner_id=other_owner_id)
    response = client.delete(
        f"{settings.API_V1_STR}/books/{book.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
