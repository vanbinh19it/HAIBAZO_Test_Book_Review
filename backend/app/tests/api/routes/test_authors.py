from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, func, select

from app.core.config import settings
from app.models import Author
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


def test_create_author_duplicate_after_normalize_name(
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
        json={"name": f"  {data['name']}  "},
    )
    assert second.status_code == 400
    assert second.json()["detail"] == "Author already exists"


def test_create_author_trims_name(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    raw_name = f"  author-{random_lower_string()}  "
    response = client.post(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        json={"name": raw_name},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == raw_name.strip()


def test_read_authors_pagination_metadata(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    baseline_count = db.exec(
        select(func.count()).select_from(Author).where(Author.owner_id == current_user_id)
    ).one()
    for _ in range(6):
        create_random_author(db, owner_id=current_user_id)

    response = client.get(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        params={"page": 2, "page_size": 5},
    )
    assert response.status_code == 200
    content = response.json()
    expected_count = baseline_count + 6
    assert content["count"] == expected_count
    assert content["page"] == 2
    assert content["limit"] == 5
    assert content["total_pages"] == (expected_count + 4) // 5
    expected_items_on_page = max(min(expected_count - 5, 5), 0)
    assert len(content["data"]) == expected_items_on_page


def test_read_authors_sorted_by_created_at_ascending(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    current_user_id = _get_current_user_id(client, normal_user_token_headers)
    base = datetime.now(timezone.utc)
    older = Author(
        name=f"older-{random_lower_string()}",
        owner_id=current_user_id,
        created_at=base - timedelta(days=2),
    )
    middle = Author(
        name=f"middle-{random_lower_string()}",
        owner_id=current_user_id,
        created_at=base - timedelta(days=1),
    )
    newer = Author(
        name=f"newer-{random_lower_string()}",
        owner_id=current_user_id,
        created_at=base,
    )
    db.add(older)
    db.add(middle)
    db.add(newer)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        params={"page": 1, "page_size": 100},
    )
    assert response.status_code == 200
    names = [item["name"] for item in response.json()["data"]]
    older_index = names.index(older.name)
    middle_index = names.index(middle.name)
    newer_index = names.index(newer.name)
    assert older_index < middle_index < newer_index


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

    first_page_response = client.get(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        params={"page": 1, "page_size": 100},
    )
    assert first_page_response.status_code == 200
    first_page_content = first_page_response.json()
    assert first_page_content["total_pages"] >= 1

    response = client.get(
        f"{settings.API_V1_STR}/authors/",
        headers=normal_user_token_headers,
        params={"page": first_page_content["total_pages"], "page_size": 100},
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
