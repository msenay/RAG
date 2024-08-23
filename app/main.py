import logging
import os
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import qa

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
API_PORT = int(os.getenv("API_PORT", 8001))
app = FastAPI()

STATIC_DIR = os.getenv("STATIC_DIR", "static")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "templates")


# Include routers
app.include_router(qa.router, tags=["qa"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Exception handler for validation errors.

    Args:
        request: request.
        exc: raised error.

    Returns:
        JSONResponse: details about the validation error.
    """
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/ping")
async def ping():
    """
    Ping endpoint to check the service status.
    This endpoint is used to verify if the service is running.
    It returns a simple "pong" message.
    Returns:
        str: A "pong" message.
    """
    return "pong"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
