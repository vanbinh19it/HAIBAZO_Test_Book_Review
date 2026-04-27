from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.author import create_random_author
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import random_email, random_lower_string


def _get_current_user_id(client: TestClient, headers: dict[str, str]) -> str:
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_create_author_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": f"author-{random_lower_string()}"}
    response = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
    assert content["books_count"] == 0
    assert content["owner_id"] == _get_current_user_id(client, superuser_token_headers)


def test_create_author_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"name": f"author-{random_lower_string()}"}
    response = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
    assert content["books_count"] == 0
    assert content["owner_id"] == _get_current_user_id(client, normal_user_token_headers)


def test_create_author_duplicate_same_owner(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"name": f"author-{random_lower_string()}"}
    first = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert first.status_code == 200

    second = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert second.status_code == 400
    assert second.json()["detail"] == "Author already exists"


def test_create_author_same_name_different_owner_allowed(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    data = {"name": f"author-{random_lower_string()}"}
    first = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert first.status_code == 200

    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    second = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=other_headers,
        json=data,
    )
    assert second.status_code == 200
    assert second.json()["name"] == data["name"]


def test_read_author_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/authors/999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"


def test_read_author_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    author = create_random_author(db, owner_id=other_owner_id)

    response = client.get(
        f"{settings.API_V1_STR}/authors/{author.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_authors_scoped_for_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    own_author = create_random_author(db, owner_id=current_user_id)

    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    create_random_author(db, owner_id=other_owner_id)

    response = client.get(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    author_ids = {item["id"] for item in content["data"]}
    assert own_author.id in author_ids
    for item in content["data"]:
        assert item["owner_id"] == current_user_id


def test_update_author(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    author = create_random_author(db, owner_id=current_user_id)
    data = {"name": f"updated-{random_lower_string()}"}
    response = client.put(
        f"{settings.API_V1_STR}/authors/{author.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == author.id
    assert content["name"] == data["name"]
    assert content["owner_id"] == current_user_id


def test_update_author_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    author = create_random_author(db, owner_id=other_owner_id)
    data = {"name": f"updated-{random_lower_string()}"}
    response = client.put(
        f"{settings.API_V1_STR}/authors/{author.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_delete_author(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    author = create_random_author(db, owner_id=current_user_id)
    response = client.delete(
        f"{settings.API_V1_STR}/authors/{author.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Author deleted successfully"


def test_delete_author_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    other_owner_id = _get_current_user_id(client, other_headers)
    author = create_random_author(db, owner_id=other_owner_id)
    response = client.delete(
        f"{settings.API_V1_STR}/authors/{author.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
