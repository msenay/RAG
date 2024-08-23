"""Database module."""
import logging

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import settings

logger = logging.getLogger(__name__)

DB_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

print(DB_URL)
logger.info(f"init settings.db_url {DB_URL}")

Base = declarative_base()
metadata = MetaData()
engine = create_engine(DB_URL, pool_pre_ping=True)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_and_create_pgvector_extension():
    with DBSession() as session:
        # pgvector existence check
        result = session.execute(text("SELECT EXISTS(SELECT * FROM pg_extension WHERE extname = 'vector');"))
        exists = result.fetchone()[0]

        if not exists:
            # pgvector creation
            session.execute(text("CREATE EXTENSION vector;"))
            session.commit()
            logger.info("pgvector extension has been created.")
        else:
            logger.warning("pgvector extension already exists.")


try:
    check_and_create_pgvector_extension()
except Exception as e:
    logger.warning(f"unable to create pgvector extension! {e}")
