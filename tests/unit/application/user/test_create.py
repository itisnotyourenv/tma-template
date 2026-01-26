from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.user.create import (
    CreateUserInputDTO,
    CreateUserInteractor,
    CreateUserOutputDTO,
)
from src.domain.user import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username


class TestCreateUserInteractor:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()

    @pytest.fixture
    def mock_transaction_manager(self):
        return Mock()

    @pytest.fixture
    def mock_auth_service(self):
        return Mock()

    @pytest.fixture
    def interactor(
        self,
        mock_user_repository,
        mock_auth_service,
        mock_transaction_manager,
    ) -> CreateUserInteractor:
        return CreateUserInteractor(
            user_repository=mock_user_repository,
            auth_service=mock_auth_service,
            transaction_manager=mock_transaction_manager,
        )

    @pytest.fixture
    def sample_create_user_input_dto(self) -> CreateUserInputDTO:
        return CreateUserInputDTO(
            id=456,
            username="testuser",
            first_name="John",
            last_name="Doe",
            is_premium=False,
            photo_url="http://example.com/photo.jpg",
        )

    @pytest.fixture
    def sample_create_user_input_dto_no_optional(self) -> CreateUserInputDTO:
        return CreateUserInputDTO(
            id=789,
            username=None,
            first_name="Jane",
            last_name=None,
            is_premium=True,
            photo_url=None,
        )

    @pytest.fixture
    def sample_user(self) -> User:
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
    def sample_user_no_optional(self) -> User:
        now = datetime.now(UTC)
        return User(
            id=UserId(789),
            username=None,
            first_name=FirstName("Jane"),
            last_name=None,
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

    async def test_create_new_user_success(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == sample_create_user_input_dto.id
        assert result.username == sample_create_user_input_dto.username
        assert result.first_name == sample_create_user_input_dto.first_name
        assert result.last_name == sample_create_user_input_dto.last_name

        mock_user_repository.get_user.assert_awaited_once_with(UserId(456))
        mock_user_repository.create_user.assert_awaited_once()
        mock_user_repository.update_user.assert_not_called()
        mock_transaction_manager.commit.assert_awaited_once()

        create_call_args = mock_user_repository.create_user.call_args[0][0]
        assert isinstance(create_call_args, dict)
        assert create_call_args["id"] == sample_create_user_input_dto.id
        assert create_call_args["username"] == sample_create_user_input_dto.username
        assert create_call_args["first_name"] == sample_create_user_input_dto.first_name
        assert create_call_args["last_name"] == sample_create_user_input_dto.last_name

    async def test_create_new_user_with_no_optional_fields_success(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto_no_optional,
        sample_user_no_optional,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(
            return_value=sample_user_no_optional
        )
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto_no_optional)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == sample_create_user_input_dto_no_optional.id
        assert result.username is None
        assert result.first_name == sample_create_user_input_dto_no_optional.first_name
        assert result.last_name is None

        mock_user_repository.get_user.assert_awaited_once_with(UserId(789))
        mock_user_repository.create_user.assert_awaited_once()
        mock_transaction_manager.commit.assert_awaited_once()

    async def test_update_existing_user_success(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)
        mock_user_repository.update_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == sample_user.id.value
        assert (
            result.username == sample_user.username.value
            if sample_user.username
            else None
        )
        assert result.first_name == sample_user.first_name.value
        assert (
            result.last_name == sample_user.last_name.value
            if sample_user.last_name
            else None
        )

        mock_user_repository.get_user.assert_awaited_once_with(UserId(456))
        mock_user_repository.create_user.assert_not_called()
        mock_user_repository.update_user.assert_awaited_once()
        mock_transaction_manager.commit.assert_awaited_once()

        update_call_args = mock_user_repository.update_user.call_args[1]
        assert update_call_args["user_id"] == UserId(456)
        assert update_call_args["username"] == sample_create_user_input_dto.username
        assert update_call_args["first_name"] == sample_create_user_input_dto.first_name
        assert update_call_args["last_name"] == sample_create_user_input_dto.last_name
        assert update_call_args["is_premium"] == sample_create_user_input_dto.is_premium
        assert update_call_args["photo_url"] == sample_create_user_input_dto.photo_url

    async def test_update_existing_user_with_no_optional_fields_success(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto_no_optional,
        sample_user_no_optional,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user_no_optional)
        mock_user_repository.update_user = AsyncMock(
            return_value=sample_user_no_optional
        )
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto_no_optional)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == sample_user_no_optional.id.value
        assert result.username is None
        assert result.first_name == sample_user_no_optional.first_name.value
        assert result.last_name is None

        mock_user_repository.get_user.assert_awaited_once_with(UserId(789))
        mock_user_repository.update_user.assert_awaited_once()
        mock_transaction_manager.commit.assert_awaited_once()

    async def test_repository_get_user_exception_propagated(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
    ):
        mock_user_repository.get_user = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_create_user_input_dto)

        assert "Database connection failed" in str(exc_info.value)
        mock_user_repository.create_user.assert_not_called()
        mock_user_repository.update_user.assert_not_called()
        mock_transaction_manager.commit.assert_not_called()

    async def test_repository_create_user_exception_propagated(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(
            side_effect=Exception("Failed to create user")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_create_user_input_dto)

        assert "Failed to create user" in str(exc_info.value)
        mock_transaction_manager.commit.assert_not_called()

    async def test_repository_update_user_exception_propagated(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)
        mock_user_repository.update_user = AsyncMock(
            side_effect=Exception("Failed to update user")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_create_user_input_dto)

        assert "Failed to update user" in str(exc_info.value)
        mock_transaction_manager.commit.assert_not_called()

    async def test_transaction_manager_exception_propagated(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock(
            side_effect=Exception("Transaction commit failed")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_create_user_input_dto)

        assert "Transaction commit failed" in str(exc_info.value)

    @pytest.mark.parametrize("user_id_value", [1, 999999999, 123])
    async def test_various_user_ids(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        user_id_value,
    ):
        input_dto = CreateUserInputDTO(
            id=user_id_value,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_premium=False,
            photo_url="http://example.com/photo.jpg",
        )

        now = datetime.now(UTC)
        created_user = User(
            id=UserId(user_id_value),
            username=Username("testuser"),
            first_name=FirstName("Test"),
            last_name=LastName("User"),
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(return_value=created_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(input_dto)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == user_id_value
        mock_user_repository.get_user.assert_awaited_once_with(UserId(user_id_value))
        mock_user_repository.create_user.assert_awaited_once()

    async def test_user_id_conversion(
        self,
        interactor,
        mock_user_repository,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock()

        await interactor(sample_create_user_input_dto)

        get_user_call_args = mock_user_repository.get_user.call_args[0][0]
        assert isinstance(get_user_call_args, UserId)
        assert get_user_call_args.value == sample_create_user_input_dto.id


class TestCreateUserInputDTO:
    def test_input_dto_creation(self):
        dto = CreateUserInputDTO(
            id=456,
            username="testuser",
            first_name="John",
            last_name="Doe",
            is_premium=False,
            photo_url="http://example.com/photo.jpg",
        )

        assert dto.id == 456
        assert dto.username == "testuser"
        assert dto.first_name == "John"
        assert dto.last_name == "Doe"
        assert dto.is_premium is False
        assert dto.photo_url == "http://example.com/photo.jpg"

    def test_input_dto_with_none_values(self):
        dto = CreateUserInputDTO(
            id=789,
            username=None,
            first_name="Jane",
            last_name=None,
            is_premium=True,
            photo_url=None,
        )

        assert dto.id == 789
        assert dto.username is None
        assert dto.first_name == "Jane"
        assert dto.last_name is None
        assert dto.is_premium is True
        assert dto.photo_url is None


class TestCreateUserOutputDTO:
    def test_output_dto_creation(self):
        dto = CreateUserOutputDTO(
            id=456,
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

        assert dto.id == 456
        assert dto.username == "testuser"
        assert dto.first_name == "John"
        assert dto.last_name == "Doe"

    def test_output_dto_with_none_values(self):
        dto = CreateUserOutputDTO(
            id=789,
            username=None,
            first_name="Jane",
            last_name=None,
        )

        assert dto.id == 789
        assert dto.username is None
        assert dto.first_name == "Jane"
        assert dto.last_name is None
