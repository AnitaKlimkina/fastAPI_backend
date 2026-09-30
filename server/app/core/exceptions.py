import logging

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "result": False,
                "error_type": "HTTPException",
                "error_message": str(exc.detail),
            }
        )

    @app.exception_handler(RequestValidationError)
    async def request_exc_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "result": False,
                "error_type": "ValidationError",
                "error_message": str(exc.errors()),
            }
        )

    @app.exception_handler(Exception)
    async def general_axc_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled error on {request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        )
