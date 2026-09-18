"""Shared API router aggregation."""

from fastapi import APIRouter, Depends

from app.api.tokens import router as tokens_router
from app.auth.deps import get_auth_context

# All routes mounted on this router require a valid Bearer API token.
api_router = APIRouter(dependencies=[Depends(get_auth_context)])
api_router.include_router(tokens_router)
