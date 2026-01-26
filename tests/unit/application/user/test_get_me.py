from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.user.get_me import (
    GetUserProfileInputDTO,
    GetUserProfileInteractor,
    GetUserProfileOutputDTO,
)
from src.domain.user import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username


class TestGetUserProfileInteractor:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()

    @pytest.fixture
    def interactor(
        self,
        mock_user_repository,
    ) -> GetUserProfileInteractor:
        return GetUserProfileInteractor(
            user_repository=mock_user_repository,
        )

    @pytest.fixture
    def sample_input_dto(self) -> GetUserProfileInputDTO:
        return GetUserProfileInputDTO(user_id=UserId(456))

    @pytest.fixture
    def sample_user_with_all_fields(self) -> User:
        now = datetime.now(UTC)
        return User(
            id=UserId(456),
            username=Username("testuser"),
            first_name=FirstName("John"),
            last_name=LastName("Doe"),
            bio=Bio("Test bio"),
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

    @pytest.fixture
    def sample_user_with_optional_none(self) -> User:
        now = datetime.now(UTC)
        return User(
            id=UserId(456),
            username=None,
            first_name=FirstName("John"),
            last_name=None,
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

    async def test_get_user_profile_success_with_all_fields(
        self,
        interactor,
        mock_user_repository,
        sample_input_dto,
        sample_user_with_all_fields,
    ):
        mock_user_repository.get_user = AsyncMock(
            return_value=sample_user_with_all_fields
        )

        result = await interactor(sample_input_dto)

        assert isinstance(result, GetUserProfileOutputDTO)
        assert result.id == 456
        assert result.username == "testuser"
        assert result.first_name == "John"
        assert result.last_name == "Doe"

        mock_user_repository.get_user.assert_awaited_once_with(UserId(456))

    async def test_get_user_profile_success_with_optional_none(
        self,
        interactor,
        mock_user_repository,
        sample_input_dto,
        sample_user_with_optional_none,
    ):
        mock_user_repository.get_user = AsyncMock(
            return_value=sample_user_with_optional_none
        )

        result = await interactor(sample_input_dto)

        assert isinstance(result, GetUserProfileOutputDTO)
        assert result.id == 456
        assert result.username is None
        assert result.first_name == "John"
        assert result.last_name is None

        mock_user_repository.get_user.assert_awaited_once_with(UserId(456))

    async def test_get_user_profile_user_not_found(
        self,
        interactor,
        mock_user_repository,
        sample_input_dto,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=None)

        with pytest.raises(NotImplementedError):
            await interactor(sample_input_dto)

        mock_user_repository.get_user.assert_awaited_once_with(UserId(456))

    async def test_get_user_profile_repository_exception(
        self,
        interactor,
        mock_user_repository,
        sample_input_dto,
    ):
        mock_user_repository.get_user = AsyncMock(
            side_effect=Exception("Database error")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_input_dto)

        assert "Database error" in str(exc_info.value)
        mock_user_repository.get_user.assert_awaited_once_with(UserId(456))

    @pytest.mark.parametrize("user_id_value", [1, 999999999, 123])
    async def test_various_user_ids(
        self,
        interactor,
        mock_user_repository,
        user_id_value,
    ):
        input_dto = GetUserProfileInputDTO(user_id=UserId(user_id_value))

        now = datetime.now(UTC)
        user = User(
            id=UserId(user_id_value),
            username=Username("testuser"),
            first_name=FirstName("Test"),
            last_name=LastName("User"),
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

        mock_user_repository.get_user = AsyncMock(return_value=user)

        result = await interactor(input_dto)

        assert isinstance(result, GetUserProfileOutputDTO)
        assert result.id == user_id_value
        mock_user_repository.get_user.assert_awaited_once_with(UserId(user_id_value))


class TestGetUserProfileInputDTO:
    def test_input_dto_creation(self):
        dto = GetUserProfileInputDTO(user_id=UserId(456))

        assert dto.user_id == UserId(456)
        assert dto.user_id.value == 456


class TestGetUserProfileOutputDTO:
    def test_output_dto_creation(self):
        dto = GetUserProfileOutputDTO(
            id=456,
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

        assert dto.id == 456
        assert dto.username == "testuser"
        assert dto.first_name == "John"
        assert dto.last_name == "Doe"
