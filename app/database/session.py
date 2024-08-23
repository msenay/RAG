from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import sessionmaker
from app.database import engine


def get_db() -> Generator:
    """Provide a context manager for database sessions using SQLAlchemy's sessionmaker.

    Yields:
        Session: database session.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # or db.pop()


db_context = contextmanager(get_db)
