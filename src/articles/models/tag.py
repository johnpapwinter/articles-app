from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.articles.models.base import BaseModel


class Tag(BaseModel):
    __tablename__ = 'tags'
    __versioned__ = {
        'transaction_table_schema': 'versioning'
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


    articles: Mapped[List["Article"]] = relationship(
        secondary="article_tags",
        back_populates="tags",
    )


