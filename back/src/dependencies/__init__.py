"""Dependencies module."""
from .authentication import get_current_customer
from .database import get_db_session

__all__ = ["get_current_customer", "get_db_session"]
