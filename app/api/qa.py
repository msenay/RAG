import requests
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.database.session import get_db
from app.database import crud
from app.huggingface.manager import ModelManager
from app.models.document import DocumentStatusEnum, DocumentEventsEnum, UploadDocumentResponse, QAResponse, QARequest, \
    UploadDocumentRequest
from app.settings import settings
from app.tasks.document import move_document_forward
import os
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

router = APIRouter()

model_manager = ModelManager()
embedding_model = model_manager.get_model()


def pad_or_truncate_vector(vector, target_length):
    """Pad or truncate the vector to the target length."""
    if len(vector) > target_length:
        return vector[:target_length]
    elif len(vector) < target_length:
        return np.pad(vector, (0, target_length - len(vector)), 'constant')
    return vector


@router.post("/upload/", response_model=UploadDocumentResponse)
async def upload_document(
        request: UploadDocumentRequest,
        db_session: Session = Depends(get_db)
) -> JSONResponse:
    """Endpoint for uploading a document from a URL and processing it.

    Args:
        request (UploadDocumentRequest): The URL of the PDF to be uploaded and processed.
        db_session (Session): Database session.

    Returns:
        JSONResponse: Response containing the document ID and status.
    """

    # Fetch and save the file locally from the URL
    os.makedirs(settings.pdfs_data_dir, exist_ok=True)
    response = requests.get(request.url)
    logger.info(f"response of pdf url request {response=}")
    file_name = request.url.split("/")[-1]
    logger.info(f"file_name {file_name=}")
    file_path = f"{settings.pdfs_data_dir}/{file_name}"
    logger.info(f"file_path {file_path=}")

    with open(file_path, "wb") as f:
        f.write(response.content)

    logger.info(f"File saved at {file_path}. Exists: {os.path.isfile(file_path)}")

    # Insert document record into the database
    document_id = crud.insert_document(db_session, file_path)
    logger.info("document inserted")

    # Move document forward in the processing pipeline
    move_document_forward(document_id, DocumentEventsEnum.LOAD_REQUEST.value)

    # Retrieve the updated document information
    document = crud.get_document(db_session, document_id)
    if document:
        response = UploadDocumentResponse(document_id=document_id, status=document.status)
        return JSONResponse(content=jsonable_encoder(response), status_code=200)
    else:
        raise HTTPException(status_code=400, detail="Unable to upload and process the document.")


@router.post("/qa/", response_model=QAResponse)
async def question_answer(
        request: QARequest,
        db_session: Session = Depends(get_db)
) -> JSONResponse:
    """Endpoint for answering a query based on the processed document."""

    # Retrieve the document based on URL (assuming the document was already processed)
    document = crud.get_document_by_url(db_session, request.url)
    if not document or document.status != DocumentStatusEnum.INDEXED:
        raise HTTPException(status_code=404, detail="Document not found or not yet processed.")

    # Embed the query using the same embedding model
    query_embedding = embedding_model(request.query)[0]
    query_embedding = np.array(query_embedding).flatten()

    # Determine the target length (e.g., based on the first chunk or a set value)
    target_length = 16000  # Assuming this is your standard chunk length

    # Adjust the query embedding to match the target length
    query_embedding = pad_or_truncate_vector(query_embedding, target_length)

    # Retrieve and process chunks individually
    similarities = []
    for chunk in crud.get_chunks_individually(db_session, document_id=document.id):
        chunk_vector = np.array(chunk.vector).flatten()
        chunk_vector = pad_or_truncate_vector(chunk_vector, target_length)

        similarity = cosine_similarity(query_embedding.reshape(1, -1), chunk_vector.reshape(1, -1))[0][0]
        similarities.append((chunk.text, similarity))

    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return the top 5 most relevant chunks
    relevant_chunks = [text for text, _ in similarities[:5]]
    response = QAResponse(relevant_chunks=relevant_chunks)
    return JSONResponse(content=jsonable_encoder(response), status_code=200)
