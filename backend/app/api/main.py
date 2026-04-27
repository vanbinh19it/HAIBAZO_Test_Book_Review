from fastapi import APIRouter

from app.api.routes import authors, books, items, login, private, reviews, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(authors.router)
api_router.include_router(books.router)
api_router.include_router(reviews.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
