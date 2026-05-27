from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _error_code(message: str) -> str:
    return (
        message.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("<=", "lte")
    )


def error_payload(status_code: int, message: str) -> dict:
    return {
        "error": _error_code(message),
        "message": message,
        "status_code": status_code,
    }


async def http_exception_handler(request: Request, exc: HTTPException):
    message = str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.status_code, message),
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "status_code": 422,
            "details": exc.errors(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
