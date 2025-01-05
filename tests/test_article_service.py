from io import BytesIO

import pytest
import pandas as pd
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

        async def test_export_search_to_csv_empty_results(self, article_service):
            # Arrange
            search_filters = ArticleSearchFilters()

            # Act
            csv_buffer = await article_service.export_search_to_csv(search_params=search_filters)

            # Assert
            assert isinstance(csv_buffer, BytesIO)
            # Read the CSV data
            csv_buffer.seek(0)
            df = pd.read_csv(csv_buffer)
            assert len(df) == 0
            assert list(df.columns) == ['ID', 'Title', 'Abstract', 'Publication Date', 'Authors', 'Tags', 'Owner ID']

        async def test_export_search_to_csv_with_results(self, article_service):
            # Arrange
            # Create test author and tag
            author = await article_service.author_repository.create(AuthorCreate(
                name="Test Author"
            ))
            tag = await article_service.tag_repository.create(TagCreate(
                name="Test Tag"
            ))

            # Create test article
            article_data = ArticleCreate(
                title="Test Article",
                abstract="Test Abstract",
                publication_date=datetime.now(timezone.utc),
                owner_id=1,
                author_ids=[author.id],
                tag_ids=[tag.id]
            )
            await article_service.create(obj=article_data)

            search_filters = ArticleSearchFilters(
                title="Test"
            )

            # Act
            csv_buffer = await article_service.export_search_to_csv(search_params=search_filters)

            # Assert
            assert isinstance(csv_buffer, BytesIO)
            # Read the CSV data
            csv_buffer.seek(0)
            df = pd.read_csv(csv_buffer)
            assert len(df) >= 1

            # Check first row content
            first_row = df.iloc[0]
            assert first_row['Title'] == "Test Article"
            assert first_row['Abstract'] == "Test Abstract"
            assert first_row['Authors'] == "Test Author"
            assert first_row['Tags'] == "Test Tag"
            assert first_row['Owner ID'] == 1

        async def test_export_search_to_csv_with_filters(self, article_service):
            # Arrange
            # Create multiple articles with different titles
            article_data1 = ArticleCreate(
                title="Python Article",
                abstract="Python Abstract",
                publication_date=datetime.now(timezone.utc),
                owner_id=1,
                author_ids=[],
                tag_ids=[]
            )
            article_data2 = ArticleCreate(
                title="Java Article",
                abstract="Java Abstract",
                publication_date=datetime.now(timezone.utc),
                owner_id=1,
                author_ids=[],
                tag_ids=[]
            )
            await article_service.create(obj=article_data1)
            await article_service.create(obj=article_data2)

            search_filters = ArticleSearchFilters(
                title="Python"
            )

            # Act
            csv_buffer = await article_service.export_search_to_csv(search_params=search_filters)

            # Assert
            assert isinstance(csv_buffer, BytesIO)
            csv_buffer.seek(0)
            df = pd.read_csv(csv_buffer)

            # Check that only Python article is included
            assert len(df[df['Title'].str.contains('Python', na=False)]) == 1
            assert len(df[df['Title'].str.contains('Java', na=False)]) == 0

        async def test_export_search_to_csv_with_abstract_search(self, article_service):
            # Arrange
            article_data = ArticleCreate(
                title="Test Article",
                abstract="Specific unique abstract for testing",
                publication_date=datetime.now(timezone.utc),
                owner_id=1,
                author_ids=[],
                tag_ids=[]
            )
            await article_service.create(obj=article_data)

            search_filters = ArticleSearchFilters(
                abstract_search="unique"
            )

            # Act
            csv_buffer = await article_service.export_search_to_csv(search_params=search_filters)

            # Assert
            assert isinstance(csv_buffer, BytesIO)
            csv_buffer.seek(0)
            df = pd.read_csv(csv_buffer)
            assert len(df) >= 1
            assert "unique" in df.iloc[0]['Abstract'].lower()

        async def test_export_search_to_csv_encoding(self, article_service):
            # Arrange
            # Create article with special characters
            article_data = ArticleCreate(
                title="Test with üñíçødé",
                abstract="Abstract with émôjîs 🌟",
                publication_date=datetime.now(timezone.utc),
                owner_id=1,
                author_ids=[],
                tag_ids=[]
            )
            await article_service.create(obj=article_data)

            search_filters = ArticleSearchFilters()

            # Act
            csv_buffer = await article_service.export_search_to_csv(search_params=search_filters)

            # Assert
            assert isinstance(csv_buffer, BytesIO)
            csv_buffer.seek(0)
            df = pd.read_csv(csv_buffer, encoding='utf-8-sig')
            assert "üñíçødé" in df.iloc[0]['Title']
            assert "émôjîs" in df.iloc[0]['Abstract']

