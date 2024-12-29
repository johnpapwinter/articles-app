import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from src.articles.schemas.author import AuthorCreate, AuthorUpdate
from src.articles.services.author import AuthorService
from tests.mocks import MockAuthorRepository


@pytest.fixture
def author_service():
    # Create an empty AsyncSession mock since we won't use it
    db_session = MagicMock()

    # Initialize the service with our mock repository
    service = AuthorService(db_session)
    service.repository = MockAuthorRepository()

    return service


@pytest.mark.asyncio
class TestAuthorService:
    async def test_create_author(self, author_service):
        # Arrange
        author_data = AuthorCreate(
            name="Test Author"
        )

        # Act
        author = await author_service.create(obj=author_data)

        # Assert
        assert author is not None
        assert author.id is not None
        assert author.name == "Test Author"
        assert author.created_at is not None
        assert author.updated_at is not None

    async def test_create_duplicate_author(self, author_service):
        # Arrange
        author_data = AuthorCreate(
            name="Test Author"
        )
        original_author = await author_service.create(obj=author_data)

        # Act
        duplicate_author = await author_service.create(obj=author_data)

        # Assert
        assert duplicate_author.id == original_author.id
        assert duplicate_author.name == original_author.name

    async def test_get_author_by_id(self, author_service):
        # Arrange
        author_data = AuthorCreate(
            name="Test Author"
        )
        created_author = await author_service.create(obj=author_data)

        # Act
        retrieved_author = await author_service.get_by_id(created_author.id)

        # Assert
        assert retrieved_author is not None
        assert retrieved_author.id == created_author.id
        assert retrieved_author.name == created_author.name

    async def test_get_nonexistent_author(self, author_service):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await author_service.get_by_id(999)
        assert exc_info.value.status_code == 404

