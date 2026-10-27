import logging

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


async def http_exc_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": "HTTPException",
            "error_message": str(exc.detail),
        }
    )


async def request_exc_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "result": False,
            "error_type": "ValidationError",
            "error_message": str(exc.errors()),
        }
    )


async def general_exc_handler(req: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", req.method, req.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "result": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(
        HTTPException,
        http_exc_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError,
        request_exc_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, general_exc_handler)
