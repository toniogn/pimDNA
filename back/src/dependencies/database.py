"""Database dependency module."""
from typing import Iterator

from sqlalchemy.orm import Session

from ..database import make_db_session
from ..logger import Logger

logger = Logger(__name__)


def get_db_session() -> Iterator[Session]:
    """Get database session.

    Used as a dependency in the API routes.

    Yields:
        Session: Database session.

    Raises:
        Exception: If the database session fails.
    """
    db_session = make_db_session()
    try:
        yield db_session
    except Exception as exception:
        logger.critical(
            "rolling back db session due to %s",
            exception,
            exc_info=True,
        )
        db_session.rollback()
        raise exception
    finally:
        db_session.close()
