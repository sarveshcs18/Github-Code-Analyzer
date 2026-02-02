from fastapi import APIRouter
from app.api.api_v1.endpoints import repo

api_router = APIRouter()

api_router.include_router(repo.router, prefix="/repo", tags=["repo"])
