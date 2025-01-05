from typing import Callable
from fastapi import Request
from starlette.responses import Response

from src.articles.utils.logging import setup_logging

logger = setup_logging(__name__)


async def logger_middleware(request: Request, call_next: Callable) -> Response:
    logger.info(f"Request started: {request.method} {request.url}")

    response = await call_next(request)

    logger.info(
        f"Request processed: {request.method} {request.url} "
        f"- Status code: {response.status_code} "
    )

    return response

