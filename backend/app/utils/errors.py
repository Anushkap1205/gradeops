from fastapi import Request
from fastapi.responses import JSONResponse


async def json_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "An unexpected error occurred"},
    )
