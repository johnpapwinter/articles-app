import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from src.articles.schemas.tag import TagCreate, TagUpdate
from src.articles.services.tag import TagService
from tests.mocks import MockTagRepository


@pytest.fixture
def tag_service():
    # Create an empty AsyncSession mock since we won't use it
    db_session = MagicMock()

    # Initialize the service with our mock repository
    service = TagService(db_session)
    service.repository = MockTagRepository()

    return service


@pytest.mark.asyncio
class TestTagService:
    async def test_create_tag(self, tag_service):
        # Arrange
        tag_data = TagCreate(
            name="Test Tag"
        )

        # Act
        tag = await tag_service.create(obj=tag_data)

        # Assert
        assert tag is not None
        assert tag.id is not None
        assert tag.name == "Test Tag"
        assert tag.created_at is not None
        assert tag.updated_at is not None

    async def test_create_duplicate_tag(self, tag_service):
        # Arrange
        tag_data = TagCreate(
            name="Test Tag"
        )
        original_tag = await tag_service.create(obj=tag_data)

        # Act
        duplicate_tag = await tag_service.create(obj=tag_data)

        # Assert
        assert duplicate_tag.id == original_tag.id
        assert duplicate_tag.name == original_tag.name

    async def test_get_tag_by_id(self, tag_service):
        # Arrange
        tag_data = TagCreate(
            name="Test Tag"
        )
        created_tag = await tag_service.create(obj=tag_data)

        # Act
        retrieved_tag = await tag_service.get_by_id(created_tag.id)

        # Assert
        assert retrieved_tag is not None
        assert retrieved_tag.id == created_tag.id
        assert retrieved_tag.name == created_tag.name

    async def test_get_nonexistent_tag(self, tag_service):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await tag_service.get_by_id(999)
        assert exc_info.value.status_code == 404


