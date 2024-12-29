import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi import HTTPException

from src.articles.schemas.article import ArticleCreate, ArticleUpdate, ArticleSearchFilters
from src.articles.schemas.author import AuthorCreate
from src.articles.schemas.tag import TagCreate
from src.articles.services.article import ArticleService
from tests.mocks import (
    MockArticleRepository,
    MockAuthorRepository,
    MockTagRepository,
    MockArticleSearchRepository
)


@pytest.fixture
def article_service():
    # Create an empty AsyncSession mock since we won't use it
    db_session = MagicMock()

    # Initialize the service with our mock repositories
    service = ArticleService(db_session, MockArticleSearchRepository())

    # Replace the repositories with our mocks
    service.repository = MockArticleRepository()
    service.author_repository = MockAuthorRepository()
    service.tag_repository = MockTagRepository()

    return service


@pytest.mark.asyncio
class TestArticleService:
    async def test_create_article(self, article_service):
        # Arrange
        # Create a test author and tag first
        author = await article_service.author_repository.create(AuthorCreate(
            name="Test Author"
        ))
        tag = await article_service.tag_repository.create(TagCreate(
            name="Test Tag"
        ))

        article_data = ArticleCreate(
            title="Test Article",
            abstract="Test Abstract",
            publication_date=datetime.now(timezone.utc),
            owner_id=1,
            author_ids=[author.id],
            tag_ids=[tag.id]
        )

        # Act
        article = await article_service.create(obj=article_data)

        # Assert
        assert article is not None
        assert article.title == "Test Article"
        assert article.abstract == "Test Abstract"
        assert article.owner_id == 1
        assert len(article.authors) == 1
        assert len(article.tags) == 1

    async def test_update_article(self, article_service):
        # Arrange
        # Create initial article
        author = await article_service.author_repository.create(AuthorCreate(
            name="Test Author"
        ))
        tag = await article_service.tag_repository.create(TagCreate(
            name="Test Tag"
        ))

        article_data = ArticleCreate(
            title="Test Article",
            abstract="Test Abstract",
            publication_date=datetime.now(timezone.utc),
            owner_id=1,
            author_ids=[author.id],
            tag_ids=[tag.id]
        )
        article = await article_service.create(obj=article_data)

        update_data = ArticleUpdate(
            title="Updated Article",
            abstract="Updated Abstract"
        )

        # Act
        updated_article = await article_service.update(
            obj_id=article.id,
            obj=update_data,
            user_id=1
        )

        # Assert
        assert updated_article.title == "Updated Article"
        assert updated_article.abstract == "Updated Abstract"

    async def test_update_article_unauthorized(self, article_service):
        # Arrange
        article_data = ArticleCreate(
            title="Test Article",
            abstract="Test Abstract",
            publication_date=datetime.now(timezone.utc),
            owner_id=1,
            author_ids=[],
            tag_ids=[]
        )
        article = await article_service.create(obj=article_data)

        update_data = ArticleUpdate(
            title="Updated Article"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await article_service.update(
                obj_id=article.id,
                obj=update_data,
                user_id=2  # Different user
            )
        assert exc_info.value.status_code == 403

    async def test_search_articles(self, article_service):
        # Arrange
        article_data = ArticleCreate(
            title="Test Article",
            abstract="Test Abstract",
            publication_date=datetime.now(timezone.utc),
            owner_id=1,
            author_ids=[],
            tag_ids=[]
        )
        await article_service.create(obj=article_data)

        search_filters = ArticleSearchFilters(
            abstract_search="Test"
        )

        # Act
        result = await article_service.search(
            search_params=search_filters,
            page=1,
            page_size=10
        )

        # Assert
        assert result.total_items >= 0
        assert isinstance(result.items, list)