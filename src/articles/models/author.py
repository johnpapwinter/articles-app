from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.articles.models.base import BaseModel


class Author(BaseModel):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


    articles: Mapped[List["Article"]] = relationship(
        secondary="article_authors",
        back_populates="authors",
    )

