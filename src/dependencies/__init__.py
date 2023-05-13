"""Dependencies module."""
from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from ..api.utils import User
from .authentication import AuthenticatedUser
from .database import get_db_session


def get_user(
    authenticated_user: AuthenticatedUser = Depends(),
    db_session: Session = Depends(get_db_session),
) -> Iterator[User]:
    """Get user object from the authenticated user.

    Used as a dependency in the API routes.

    Args:
        authenticated_user: Authenticated user object.
        db_session: Database session.

    Yields:
        User: User object.
    """
    yield authenticated_user.get_from_or_create_in_db(db_session)


__all__ = ["get_user", "get_db_session"]
