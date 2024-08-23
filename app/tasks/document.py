import logging
import os
from itertools import chain
from PyPDF2 import PdfReader
from types import MappingProxyType
from app.database import crud
from app.models.document import DocumentEventsEnum, DocumentStatusEnum
from app.database.session import db_context
from app.tasks import dramatiq
from app.settings import settings
from app.huggingface.manager import ModelManager

logger = logging.getLogger(__name__)

model_manager = ModelManager()
embedding_model = model_manager.get_model()


def document_state_mapping() -> MappingProxyType:
    """Mapping of document states to corresponding status-event pairs."""
    return MappingProxyType(
        {
            DocumentStatusEnum.ADDED: {
                DocumentEventsEnum.LOAD_REQUEST: download_and_chunk_document,
                DocumentEventsEnum.DELETE_REQUEST: delete_document,
            },
            DocumentStatusEnum.LOAD: {
                DocumentEventsEnum.LOAD_FINISHED: mark_as_indexed,
                DocumentEventsEnum.LOAD_FAILED: mark_as_failed,
                DocumentEventsEnum.DELETE_REQUEST: delete_document,
            },
            DocumentStatusEnum.INDEXED: {
                DocumentEventsEnum.DELETE_REQUEST: delete_document,
            },
            DocumentStatusEnum.FAILED: {
                DocumentEventsEnum.LOAD_REQUEST: download_and_chunk_document,
                DocumentEventsEnum.DELETE_REQUEST: delete_document,
            },
        }
    )


def move_document_forward(document_id: int, event: str, **kwargs) -> None:
    """Move document forward based on the current state and event."""
    logger.info(f"Moving document forward with event: {event}, kwargs: {kwargs}")

    try:
        with db_context() as db_session:
            document = crud.get_document(db_session, document_id=document_id)
        if document:
            status = document.status
            next_task = document_state_mapping()[status].get(event)
            if next_task:
                logger.info(f"Moving document {document_id} from status: {status} on event: {event} to task: {next_task}")
                next_task.send(document_id=document_id, **kwargs)
            else:
                logger.info(f"No action needed for document {document_id} on status: {status} with event: {event}")
        else:
            logger.error(f"Document not found! {document_id=}, event: {event}")
    except KeyError:
        logger.exception(f"Status mapping is not available. {status=}, event: {event=}")


@dramatiq.actor(
    max_retries=settings.dramatiq_task_max_retries,
    time_limit=settings.dramatiq_task_time_limit_ms,
    max_age=settings.dramatiq_task_max_age_ms,
)
def download_and_chunk_document(document_id: int) -> None:
    logger.info(f"Downloading and chunking document: {document_id}")

    with db_context() as db_session:
        document = crud.get_document(db_session, document_id)
        if not document:
            logger.error(f"Document not found! {document_id=}")
            return

        try:
            file_path = document.file_path
            if os.path.isfile(file_path):
                with open(file_path, "rb") as pdf_file:
                    pdf_reader = PdfReader(pdf_file)

                    if embedding_model is None:
                        logger.error("Failed to load the embedding model. embedding_model is None.")
                        raise RuntimeError("Failed to load the embedding model.")

                    logger.info("Embedding model loaded successfully.")

                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            words = text.split()
                            chunk_size = 100

                            for i in range(0, len(words), chunk_size):
                                chunk = " ".join(words[i : i + chunk_size])
                                logger.info(f"Processing chunk: {chunk}")

                                try:
                                    raw_vector = embedding_model(chunk)[0] if chunk else None
                                    logger.info(f"Raw vector length (before processing): {len(raw_vector)}")

                                    if raw_vector:
                                        # Ensure the vector is flat
                                        if isinstance(raw_vector[0], list):
                                            flat_vector = list(chain.from_iterable(raw_vector))
                                        else:
                                            flat_vector = raw_vector

                                        logger.info(f"Flattened vector length: {len(flat_vector)}")

                                        # Chunk vector if needed
                                        max_dimensions = 16000
                                        for j in range(0, len(flat_vector), max_dimensions):
                                            vector_chunk = flat_vector[j : j + max_dimensions]
                                            logger.info(f"Storing vector chunk of length: {len(vector_chunk)}")
                                            crud.insert_chunk(db_session, document_id=document_id, chunk=chunk, vector=vector_chunk)
                                except Exception as e:
                                    logger.error(f"Error generating vector for chunk: {e}")
                                    continue

                    crud.update_document_status(db_session, document_id, DocumentStatusEnum.INDEXED)
                    logger.info(f"Document {document_id} has been successfully indexed.")
            else:
                raise FileNotFoundError(f"File not found at path: {file_path}")

        except Exception as e:
            logger.error(f"Error occurred while downloading and chunking document: {e}")
            crud.update_document_status(db_session, document_id, DocumentStatusEnum.FAILED)


@dramatiq.actor(
    max_retries=settings.dramatiq_task_max_retries,
    time_limit=settings.dramatiq_task_time_limit_ms,
    max_age=settings.dramatiq_task_max_age_ms,
)
def delete_document(document_id: int) -> None:
    """Delete the document and its related data from the database."""
    logger.info(f"Deleting document: {document_id}")

    try:
        with db_context() as db_session:
            document = crud.get_document(db_session, document_id=document_id)
            if document:
                crud.delete_document(db_session, document_id=document_id)
                crud.update_document_status(db_session, document_id, DocumentStatusEnum.DELETED)
            else:
                logger.error(f"Document not found! {document_id=}")

    except Exception as e:
        logger.error(f"Error occurred while deleting document: {e}")


@dramatiq.actor(
    max_retries=settings.dramatiq_task_max_retries,
    time_limit=settings.dramatiq_task_time_limit_ms,
    max_age=settings.dramatiq_task_max_age_ms,
)
def mark_as_failed(document_id: int) -> None:
    """Mark document as failed.

    Args:
        document_id: document id to process.
    """
    logger.info(f"Marking document as failed - {document_id}")
    with db_context() as db_session:
        crud.update_document_status(db_session, document_id=document_id, status=DocumentStatusEnum.FAILED)


@dramatiq.actor(
    max_retries=settings.dramatiq_task_max_retries,
    time_limit=settings.dramatiq_task_time_limit_ms,
    max_age=settings.dramatiq_task_max_age_ms,
)
def mark_as_indexed(document_id: int) -> None:
    """Mark document as indexed.

    Args:
        document_id: document id to process.
    """
    logger.info(f"Marking document as indexed - {document_id}")
    with db_context() as db_session:
        crud.update_document_status(db_session, document_id, status=DocumentStatusEnum.INDEXED)

    logger.info(f"Document {document_id} has been successfully indexed.")
