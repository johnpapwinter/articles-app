from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.db.session import get_db


DbSession = Annotated[AsyncSession, Depends(get_db)]
