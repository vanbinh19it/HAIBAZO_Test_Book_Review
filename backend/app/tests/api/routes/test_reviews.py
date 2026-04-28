from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.book import create_random_book
from app.tests.utils.review import create_random_review
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import random_email, random_lower_string


def _get_current_user_id(client: TestClient, headers: dict[str, str]) -> str:
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_create_review(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    book = create_random_book(db, owner_id=current_user_id)
    data = {"book_id": book.id, "content": f"review-{random_lower_string()}"}
    response = client.post(
        f"{settings.API_V1_STR}/reviews/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["book_id"] == book.id
    assert content["content"] == data["content"]
    assert content["book_title"] == book.title
    assert content["owner_id"] == current_user_id


def test_create_review_trims_content(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    book = create_random_book(db, owner_id=current_user_id)
    raw_content = f"  review-{random_lower_string()}  "
    response = client.post(
        f"{settings.API_V1_STR}/reviews/",
        headers=normal_user_token_headers,
        json={"book_id": book.id, "content": raw_content},
    )
    assert response.status_code == 200
    assert response.json()["content"] == raw_content.strip()


def test_create_review_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    other_book = create_random_book(db, owner_id=other_owner_id)
    data = {"book_id": other_book.id, "content": f"review-{random_lower_string()}"}
    response = client.post(
        f"{settings.API_V1_STR}/reviews/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_review(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    review = create_random_review(db, owner_id=current_user_id)
    response = client.get(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == review.id
    assert content["book_id"] == review.book_id
    assert content["content"] == review.content
    assert content["owner_id"] == current_user_id


def test_read_review_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/reviews/999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"


def test_read_review_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    review = create_random_review(db, owner_id=other_owner_id)
    response = client.get(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_reviews_scoped_for_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    own_review = create_random_review(db, owner_id=current_user_id)

    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    create_random_review(db, owner_id=other_owner_id)

    response = client.get(
        f"{settings.API_V1_STR}/reviews/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    review_ids = {item["id"] for item in content["data"]}
    assert own_review.id in review_ids
    for item in content["data"]:
        assert item["owner_id"] == current_user_id


def test_read_reviews_sorted_old_to_new(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    first = create_random_review(db, owner_id=current_user_id)
    second = create_random_review(db, owner_id=current_user_id)
    third = create_random_review(db, owner_id=current_user_id)

    response = client.get(
        f"{settings.API_V1_STR}/reviews/",
        headers=normal_user_token_headers,
        params={"page": 1, "page_size": 100},
    )
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["data"]]
    assert ids.index(first.id) < ids.index(second.id) < ids.index(third.id)


def test_update_review(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    review = create_random_review(db, owner_id=current_user_id)
    data = {"content": f"updated-{random_lower_string()}"}
    response = client.put(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == review.id
    assert content["content"] == data["content"]
    assert content["owner_id"] == current_user_id


def test_update_review_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    review = create_random_review(db, owner_id=other_owner_id)
    data = {"content": f"updated-{random_lower_string()}"}
    response = client.put(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_update_review_content_none_returns_422(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    review = create_random_review(db, owner_id=current_user_id)
    response = client.put(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
        json={"content": None},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Review is required"


def test_delete_review(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    review = create_random_review(db, owner_id=current_user_id)
    response = client.delete(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Review deleted successfully"


def test_delete_review_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    review = create_random_review(db, owner_id=other_owner_id)
    response = client.delete(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_superuser_create_review_owner_follows_book_owner(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    owner_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    owner_id = _get_current_user_id(client, owner_headers)
    book = create_random_book(db, owner_id=owner_id)

    data = {"book_id": book.id, "content": f"review-{random_lower_string()}"}
    response = client.post(
        f"{settings.API_V1_STR}/reviews/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["book_id"] == book.id
    assert content["owner_id"] == owner_id


def test_superuser_update_review_book_realigns_owner(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    first_owner_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    first_owner_id = _get_current_user_id(client, first_owner_headers)
    second_owner_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    second_owner_id = _get_current_user_id(client, second_owner_headers)

    book_a = create_random_book(db, owner_id=first_owner_id)
    book_b = create_random_book(db, owner_id=second_owner_id)
    review = create_random_review(db, owner_id=first_owner_id, book=book_a)

    response = client.put(
        f"{settings.API_V1_STR}/reviews/{review.id}",
        headers=superuser_token_headers,
        json={"book_id": book_b.id},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["book_id"] == book_b.id
    assert content["owner_id"] == second_owner_id
