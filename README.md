# RAG

Project: Document Processing and Embedding API

Overview

This project is an API designed to process PDF documents, generate embeddings for chunks of text within these documents, and facilitate querying the documents based on these embeddings. The project utilizes FastAPI for the API framework, Dramatiq for task processing, SQLAlchemy for database interactions, and Hugging Face transformers for embedding generation.

Features

PDF Document Processing: Upload and process PDF documents, extracting text and generating embeddings for chunks of text within the documents.
Embeddings Storage: Store embeddings in a PostgreSQL database using pgvector for efficient vector similarity calculations.
Query Answering: Query the processed documents by embedding a query string and retrieving the most relevant chunks based on vector similarity.
Task Management: Asynchronous task handling with Dramatiq to manage document processing, embedding, and status tracking.
Technologies

FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.7+.
Dramatiq: A fast and reliable distributed task processing library for Python 3.
SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
PostgreSQL: A powerful, open-source object-relational database system.
pgvector: A PostgreSQL extension for vector data, enabling similarity searches.
Hugging Face Transformers: A state-of-the-art library for natural language processing tasks, including text embeddings.
Project Structure

```bash
project_root/
├── app/
│   ├── api/
│   │   ├── qa.py            # API endpoint for querying documents
│   ├── database/
│   │   ├── crud.py          # CRUD operations for the database
│   │   ├── models.py        # Database models
│   │   ├── session.py       # Database session management
│   ├── huggingface/
│   │   ├── manager.py       # Model manager for Hugging Face models
│   ├── models/
│   │   ├── document.py      # Document-related models
│   ├── tasks/
│   │   ├── document.py      # Task definitions for document processing
│   ├── settings.py          # Configuration settings
├── docker-compose.yml       # Docker Compose setup
├── Dockerfile               # Dockerfile for building the API
└── README.md                # Project documentation
```

Installation

Prerequisites
Docker and Docker Compose installed on your machine
PostgreSQL database set up with pgvector extension enabled
Steps
Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```
Set up the environment variables:
Create a .env file at the root of your project and add the necessary environment variables, such as database connection details and application settings.
Build and run the Docker containers:
```bash
docker-compose up --build
```
This will start the FastAPI server, the PostgreSQL database, and the Dramatiq worker.
Initialize the database:
After the containers are up and running, initialize the database by running the following command inside the API container:

```bash
docker exec -it <api-container-name> python -m app.database.init_db
```
Usage

1) Uploading and Processing a PDF
Upload a PDF Document:
Send a POST request to /upload/ with the URL of the PDF document.

Example:
```bash
curl -X POST "http://localhost:8001/upload/" -H "Content-Type: application/json" -d '{"url": "http://example.com/sample.pdf"}'
```
Processing the Document:
The document will be processed asynchronously. This includes downloading the PDF, extracting text, generating embeddings for each text chunk, and storing the embeddings in the database.
Querying a Processed Document
Once the document is indexed, you can query it using the following endpoint:

POST /qa/
Request payload:
```json
{
    "url": "http://example.com/sample.pdf",
    "query": "What is the main topic of the document?"
}
```
The API will return the most relevant text chunks based on the query.

Response example:
```json
{
    "relevant_chunks": [
        "The main topic of the document is...",
        "Another relevant section is..."
    ]
}
```

2) Querying a Processed Document:
Once the document is indexed, you can query it using the /qa/ endpoint to retrieve relevant text chunks based on your query.
Example:

```bash
curl -X POST "http://localhost:8001/qa/" -H "Content-Type: application/json" -d '{"url": "http://example.com/sample.pdf", "query": "What is the main topic of the document?"}'
```
Response Example:
```json
{
    "relevant_chunks": [
        "The main topic of the document is...",
        "Another relevant section is..."
    ]
}
```
Explanation: The API will take the query, embed it using the same model used for the document chunks, and then compute the similarity between the query and each chunk's embedding. The most relevant chunks are then returned in the response.

Task Workflow

The task processing workflow involves the following steps:

Document Added: When a document is uploaded, it is marked as ADDED in the database.
Load Request: The document is downloaded, and text chunks are extracted and embedded.
Indexing: Once embedding is complete, the document status is updated to INDEXED.
Querying: The indexed document can now be queried based on the embeddings stored in the database.
Error Handling

Document Not Found: If a document is not found or has not been processed, the API will return a 404 error.
Task Failures: If a task fails (e.g., due to an issue with the PDF file or embedding model), the document status is marked as FAILED, and the error is logged.
Future Enhancements

Support for More Document Formats: Extend the API to support more document formats beyond PDF.
Advanced Querying: Implement more sophisticated querying mechanisms, including semantic search.
Batch Processing: Enable batch processing for multiple documents simultaneously.
Contributing

Contributions are welcome! If you have suggestions for improvements or want to report a bug, please create an issue or submit a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for more details.

Acknowledgements

FastAPI
Dramatiq
Hugging Face Transformers
PostgreSQL
pgvector
