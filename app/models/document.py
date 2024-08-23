from enum import Enum

from pydantic import BaseModel


class DocumentStatusEnum(str, Enum):
    ADDED = "added"
    LOAD = "LOAD"
    READY_TO_BE_INDEXED = "ready_to_be_indexed"
    EXTRACTING_EMBEDDINGS = "extracting_embeddings"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class DocumentEventsEnum(str, Enum):
    DELETE_REQUEST = "delete_request"
    LOAD_REQUEST = "load_request"
    LOAD_FINISHED = "load_finished"
    LOAD_FAILED = "load_failed"
    EMBEDDING_REQUEST = "embedding_request"
    EMBEDDING_FINISHED = "embedding_finished"
    EMBEDDING_FAILED = "embedding_failed"


class UploadDocumentRequest(BaseModel):
    url: str


class UploadDocumentResponse(BaseModel):
    document_id: int
    status: DocumentStatusEnum


class QARequest(BaseModel):
    url: str
    query: str


class QAResponse(BaseModel):
    relevant_chunks: list[str]
