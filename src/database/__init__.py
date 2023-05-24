"""Database module."""
from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, registry

from ..constants import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_size=100, max_overflow=10)
make_db_session: Type[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
mapper_registry = registry()
Base = mapper_registry.generate_base()

__all__ = ["make_db_session", "engine", "Base"]
