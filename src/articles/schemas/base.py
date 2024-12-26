from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict
from typing_extensions import Generic, TypeVar

T = TypeVar('T')


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
        }
    )


class PaginationSchema(BaseSchema, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: List[T]
    current_page: int
    total_pages: int
    total_items: int
