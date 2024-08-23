import requests
import time

# Base URL for the FastAPI service
BASE_URL = "http://localhost:8001"

# PDF URL to be uploaded and processed
PDF_URL = "https://s29.q4cdn.com/175625835/files/doc_downloads/test.pdf"

# Upload the document
def upload_document(pdf_url):
    upload_endpoint = f"{BASE_URL}/upload/"
    response = requests.post(upload_endpoint, json={"url": pdf_url})
    if response.status_code == 200:
        data = response.json()
        print(f"Document uploaded successfully: {data}")
        return data['document_id']
    else:
        print(f"Failed to upload document: {response.text}")
        return None

# Perform a query on the uploaded document
def question_answer(document_url, query):
    qa_endpoint = f"{BASE_URL}/qa/"
    response = requests.post(qa_endpoint, json={"url": document_url, "query": query})
    if response.status_code == 200:
        data = response.json()
        print(f"Query results: {data['relevant_chunks']}")
    else:
        print(f"Failed to perform query: {response.text}")

if __name__ == "__main__":
    # # Upload the document and get the document ID
    # # document_id = upload_document(PDF_URL)
    #
    # if document_id:
    #     # Wait for the document to be processed
    #     time.sleep(10)  # Adjust sleep time based on processing time
    #
    #     # Perform a query on the uploaded document
    #     question_answer(PDF_URL, "What is the main topic of the document?")
    question_answer(PDF_URL, "What is the main topic of the document?")