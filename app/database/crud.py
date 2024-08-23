import logging
import os

from app.database.models import Document, ChunkEmbedding
from app.models.document import DocumentStatusEnum

from app.database import Base, DBSession, engine
from app.settings import settings

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initalize db."""
    Base.metadata.create_all(bind=engine)


def insert_document(db: DBSession, file_path: str) -> int:
    document = Document(file_path=file_path, status=DocumentStatusEnum.ADDED)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document.id


def update_document_status(db: DBSession, document_id: int, status: DocumentStatusEnum) -> None:
    document = db.query(Document).filter_by(id=document_id).first()
    if document:
        document.status = status
        db.commit()


def get_document(db: DBSession, document_id: int) -> Document:
    return db.query(Document).filter_by(id=document_id).first()


def delete_document(db: DBSession, document_id: int) -> None:
    document = db.query(Document).filter_by(id=document_id).first()
    if document:
        db.delete(document)
        db.commit()


def insert_chunk(db: DBSession, document_id: int, chunk: str, vector) -> int:
    try:
        chunk_obj = ChunkEmbedding(document_id=document_id, text=chunk, vector=vector)
        db.add(chunk_obj)
        db.commit()
        db.refresh(chunk_obj)
        return chunk_obj.id
    except Exception as e:
        logger.error(f"Failed to insert chunk into database: {e}")
        db.rollback()
        raise


def get_chunks(db: DBSession, document_id: int):
    return db.query(ChunkEmbedding).filter_by(document_id=document_id).all()


def get_chunks_individually(db: DBSession, document_id: int):
    """Generator to yield chunks one by one for a given document."""
    chunks = db.query(ChunkEmbedding).filter_by(document_id=document_id)
    for chunk in chunks:
        yield chunk


def delete_chunks_by_document_id(db: DBSession, document_id: int) -> None:
    db.query(ChunkEmbedding).filter_by(document_id=document_id).delete()
    db.commit()


def get_document_by_url(db: DBSession, url: str) -> Document:
    file_name = os.path.basename(url)
    file_path = os.path.join(settings.pdfs_data_dir, file_name)
    return db.query(Document).filter_by(file_path=file_path).first()
