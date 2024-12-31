from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, Table, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.articles.db.base import Base
from src.articles.models.base import BaseModel

article_authors = Table(
    'article_authors',
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE")),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE")),
)

article_tags = Table(
    'article_tags',
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Article(BaseModel):
    __tablename__ = 'articles'
    __versioned__ = {
        'transaction_table_schema': 'versioning'
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    publication_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship(back_populates="articles")
    authors: Mapped[List["Author"]] = relationship(
        secondary=article_authors,
        back_populates="articles"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=article_tags,
        back_populates="articles"
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan"
    )
