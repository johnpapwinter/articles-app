from datetime import datetime, timezone
from typing import Optional, List, Tuple, Any, Dict
from unittest.mock import MagicMock

from pydantic import BaseModel

from src.articles.models.article import Article
from src.articles.models.author import Author
from src.articles.models.tag import Tag
from src.articles.models.user import User

class MockBaseRepository:
    def __init__(self):
        self.data = {}
        self.current_id = 1

    async def get_by_id(self, id: int) -> Optional[Any]:
        return self.data.get(id)

    async def create(self, obj_in: Any) -> Any:
        model = self._create_model(obj_in)
        self.data[model.id] = model
        return model

    async def update(self, db_obj: Any, obj_in: dict) -> Any:
        # Convert input to dictionary if it's a Pydantic model
        update_data = self._get_data_dict(obj_in)

        # Update only the fields that are present in the update data
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        db_obj.updated_at = datetime.now(timezone.utc)
        self.data[db_obj.id] = db_obj  # Update the stored object
        return db_obj

    async def delete(self, obj_id: int) -> Any:
        obj = self.data.pop(obj_id, None)
        return obj

    def _get_next_id(self) -> int:
        current = self.current_id
        self.current_id += 1
        return current

    def _get_data_dict(self, obj_in: Any) -> Dict:
        if isinstance(obj_in, BaseModel):
            return obj_in.model_dump(exclude_unset=True)  # Only include set values
        elif isinstance(obj_in, dict):
            return obj_in
        else:
            raise ValueError(f"Unsupported input type: {type(obj_in)}")

    def _create_model(self, obj_in: Any) -> Any:
        raise NotImplementedError


class MockArticleRepository(MockBaseRepository):
    async def create_with_relationships(self, obj_in_data: dict, authors: List[Author], tags: List[Tag]) -> Article:
        article = Article(
            id=self._get_next_id(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            authors=authors,
            tags=tags,
            **obj_in_data
        )
        self.data[article.id] = article
        return article

    async def search_with_filters(self, search_params: Any, elastic_ids: Optional[List[str]],
                                page: int, page_size: int) -> Tuple[List[Article], int]:
        items = list(self.data.values())
        return items, len(items)

    def _create_model(self, obj_in: Any) -> Article:
        data = self._get_data_dict(obj_in)
        return Article(
            id=self._get_next_id(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **data
        )


class MockUserRepository(MockBaseRepository):
    async def get_by_username(self, username: str) -> Optional[User]:
        for user in self.data.values():
            if user.username == username:
                return user
        return None

    async def create_user(self, obj_in: Any) -> User:
        return await self.create(obj_in)

    def _create_model(self, obj_in: Any) -> User:
        data = self._get_data_dict(obj_in)
        return User(
            id=self._get_next_id(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **data
        )


class MockAuthorRepository(MockBaseRepository):
    async def get_by_name(self, name: str) -> Optional[Author]:
        for author in self.data.values():
            if author.name == name:
                return author
        return None

    def _create_model(self, obj_in: Any) -> Author:
        data = self._get_data_dict(obj_in)
        return Author(
            id=self._get_next_id(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **data
        )


class MockTagRepository(MockBaseRepository):
    async def get_by_name(self, name: str) -> Optional[Tag]:
        for tag in self.data.values():
            if tag.name == name:
                return tag
        return None

    def _create_model(self, obj_in: Any) -> Tag:
        data = self._get_data_dict(obj_in)
        return Tag(
            id=self._get_next_id(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **data
        )


class MockArticleSearchRepository:
    async def index_article(self, article: Article) -> dict:
        return {"_id": str(article.id), "result": "created"}

    async def verify_article_indexed(self, article_id: int) -> bool:
        return True

    async def search_articles(self, query: str, fuzzy: bool = True, size: int = 10) -> List[str]:
        return [str(i) for i in range(1, size + 1)]

