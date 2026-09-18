"""User-scoped query helpers.

Every data access path should filter by the authenticated user's id.
"""

from __future__ import annotations

import uuid
from typing import TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import DeclarativeBase

from app.database import Base

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


def user_scoped_select(model: type[ModelT], user_id: uuid.UUID) -> Select[tuple[ModelT]]:
    """Build a SELECT for ``model`` restricted to ``user_id``.

    The model must expose a ``user_id`` column.
    """
    if not hasattr(model, "user_id"):
        raise TypeError(f"{model.__name__} has no user_id column for scoping")
    return select(model).where(model.user_id == user_id)  # type: ignore[attr-defined]


def ensure_same_user(
    resource_user_id: uuid.UUID,
    authenticated_user_id: uuid.UUID,
) -> None:
    """Raise ``PermissionError`` if a resource is not owned by the user.

    Callers should translate this into an HTTP 404/403 as appropriate so
    existence of other users' rows is not leaked.
    """
    if resource_user_id != authenticated_user_id:
        raise PermissionError("Resource is not owned by the authenticated user")


# Re-export Base for type checkers that resolve model bounds.
__all__ = ["ensure_same_user", "user_scoped_select", "Base"]
