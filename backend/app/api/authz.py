import uuid

from fastapi import HTTPException

from app.models import User


def ensure_owner_or_superuser(
    *, current_user: User, entity_owner_id: uuid.UUID | None
) -> None:
    if not current_user.is_superuser and (entity_owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
