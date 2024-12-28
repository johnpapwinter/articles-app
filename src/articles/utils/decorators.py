from functools import wraps
from typing import Type, Any, Dict, Callable

from pydantic import BaseModel


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

        wrapper.__doc__ = description or func.__doc__
        wrapper.summary = summary
        wrapper.response_model = response_model
        wrapper.status_code = status_code
        wrapper.responses = default_responses

        return wrapper
    return decorator

