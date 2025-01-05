import functools
import time
from functools import wraps
from typing import Type, Any, Dict, Callable

from pydantic import BaseModel

from src.articles.utils.logging import setup_logging

logger = setup_logging("database_operations")


def endpoint_decorator(
        summary: str,
        response_model: Type[BaseModel] = None,
        status_code: int = 200,
        responses: Dict[int, Dict[str, Any]] = None,
        description: str = None,
        **kwargs
):
    """Decorator for standardizing endpoint documentation"""
    default_responses = {
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    }

    if responses:
        default_responses.update(responses)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            return response

        wrapper.__doc__ = description or func.__doc__
        wrapper.summary = summary
        wrapper.response_model = response_model
        wrapper.status_code = status_code
        wrapper.responses = default_responses

        return wrapper
    return decorator


def log_database_operations(func: Callable) -> Callable:
    """Decorator to log database operations"""
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        model_name = self.model.__name__ if hasattr(self, "model") else 'Unknown'
        operation = func.__name__

        start_time = time.perf_counter()

        try:
            result = await func(self, *args, **kwargs)
            execution_time = (time.perf_counter() - start_time) * 1000

            logger.info(
                f"Database Operation: {operation} | "
                f"Model Name: {model_name} | "
                f"Duration: {execution_time:.2f}ms"
            )

            return result

        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000

            logger.error(
                f"Database Operation: {operation} | "
                f"Model Name: {model_name} | "
                f"Duration: {execution_time:.2f}ms"
            )

            raise

    return wrapper

