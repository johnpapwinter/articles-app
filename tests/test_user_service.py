import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from src.articles.schemas.user import UserCreate
from src.articles.services.user import UserService
from tests.mocks import MockUserRepository


@pytest.fixture
def user_service():
    # Create an empty AsyncSession mock since we won't use it
    db_session = MagicMock()

    # Initialize the service with our mock repository
    service = UserService(db_session)
    service.repository = MockUserRepository()

    return service


@pytest.mark.asyncio
class TestUserService:
    async def test_create_user(self, user_service):
        # Arrange
        user_data = UserCreate(
            username="testuser",
            password="testpassword123"
        )

        # Act
        user = await user_service.create(obj=user_data)

        # Assert
        assert user is not None
        assert user.username == "testuser"
        assert user.password != "testpassword123"  # Password should be hashed

    async def test_create_duplicate_user(self, user_service):
        # Arrange
        user_data = UserCreate(
            username="testuser",
            password="testpassword123"
        )
        await user_service.create(obj=user_data)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create(obj=user_data)
        assert exc_info.value.status_code == 400

    async def test_authenticate_user_success(self, user_service):
        # Arrange
        user_data = UserCreate(
            username="testuser",
            password="testpassword123"
        )
        await user_service.create(obj=user_data)

        # Act
        authenticated_user = await user_service.authenticate(
            username="testuser",
            password="testpassword123"
        )

        # Assert
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"

    async def test_authenticate_user_wrong_password(self, user_service):
        # Arrange
        user_data = UserCreate(
            username="testuser",
            password="testpassword123"
        )
        await user_service.create(obj=user_data)

        # Act
        authenticated_user = await user_service.authenticate(
            username="testuser",
            password="wrongpassword"
        )

        # Assert
        assert authenticated_user is None

    async def test_authenticate_nonexistent_user(self, user_service):
        # Act
        authenticated_user = await user_service.authenticate(
            username="nonexistent",
            password="testpassword123"
        )

        # Assert
        assert authenticated_user is None


