from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.user.create import (
    CreateUserInputDTO,
    CreateUserInteractor,
    CreateUserOutputDTO,
)
from src.application.user.service import UserService
from src.domain.user import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username


class TestCreateUserInteractor:
    @pytest.fixture
    def mock_user_service(self):
        return Mock(spec=UserService)

    @pytest.fixture
    def mock_transaction_manager(self):
        return Mock()

    @pytest.fixture
    def interactor(
        self,
        mock_user_service,
        mock_transaction_manager,
    ) -> CreateUserInteractor:
        return CreateUserInteractor(
            user_service=mock_user_service,
            transaction_manager=mock_transaction_manager,
        )

    @pytest.fixture
    def sample_create_user_input_dto(self) -> CreateUserInputDTO:
        return CreateUserInputDTO(
            id=456,
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

    @pytest.fixture
    def sample_create_user_input_dto_no_optional(self) -> CreateUserInputDTO:
        return CreateUserInputDTO(
            id=789,
            username=None,
            first_name="Jane",
            last_name=None,
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

    async def test_create_user_success(
        self,
        interactor,
        mock_user_service,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_service.upsert_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == sample_create_user_input_dto.id
        assert result.username == sample_create_user_input_dto.username
        assert result.first_name == sample_create_user_input_dto.first_name
        assert result.last_name == sample_create_user_input_dto.last_name

        mock_user_service.upsert_user.assert_awaited_once()
        mock_transaction_manager.commit.assert_awaited_once()

    async def test_create_user_with_no_optional_fields_success(
        self,
        interactor,
        mock_user_service,
        mock_transaction_manager,
        sample_create_user_input_dto_no_optional,
        sample_user_no_optional,
    ):
        mock_user_service.upsert_user = AsyncMock(return_value=sample_user_no_optional)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto_no_optional)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == sample_create_user_input_dto_no_optional.id
        assert result.username is None
        assert result.first_name == sample_create_user_input_dto_no_optional.first_name
        assert result.last_name is None

        mock_user_service.upsert_user.assert_awaited_once()
        mock_transaction_manager.commit.assert_awaited_once()

    async def test_user_service_exception_propagated(
        self,
        interactor,
        mock_user_service,
        mock_transaction_manager,
        sample_create_user_input_dto,
    ):
        mock_user_service.upsert_user = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_create_user_input_dto)

        assert "Database connection failed" in str(exc_info.value)
        mock_transaction_manager.commit.assert_not_called()

    async def test_transaction_manager_exception_propagated(
        self,
        interactor,
        mock_user_service,
        mock_transaction_manager,
        sample_create_user_input_dto,
        sample_user,
    ):
        mock_user_service.upsert_user = AsyncMock(return_value=sample_user)
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
        mock_user_service,
        mock_transaction_manager,
        user_id_value,
    ):
        input_dto = CreateUserInputDTO(
            id=user_id_value,
            username="testuser",
            first_name="Test",
            last_name="User",
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

        mock_user_service.upsert_user = AsyncMock(return_value=created_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(input_dto)

        assert isinstance(result, CreateUserOutputDTO)
        assert result.id == user_id_value
        mock_user_service.upsert_user.assert_awaited_once()

    async def test_create_new_user_returns_is_new_true(
        self,
        interactor,
        mock_user_service,
        mock_transaction_manager,
        sample_create_user_input_dto,
    ):
        # New user has created_at == last_login_at
        now = datetime.now(UTC)
        new_user = User(
            id=UserId(456),
            username=Username("testuser"),
            first_name=FirstName("John"),
            last_name=LastName("Doe"),
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,  # Same as created_at = is_new=True
        )
        mock_user_service.upsert_user = AsyncMock(return_value=new_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto)

        assert result.is_new is True

    async def test_update_existing_user_returns_is_new_false(
        self,
        interactor,
        mock_user_service,
        mock_transaction_manager,
        sample_create_user_input_dto,
    ):
        # Existing user has last_login_at != created_at
        created = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        now = datetime.now(UTC)
        existing_user = User(
            id=UserId(456),
            username=Username("testuser"),
            first_name=FirstName("John"),
            last_name=LastName("Doe"),
            bio=None,
            created_at=created,
            updated_at=now,
            last_login_at=now,  # Different from created_at = is_new=False
        )
        mock_user_service.upsert_user = AsyncMock(return_value=existing_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_create_user_input_dto)

        assert result.is_new is False


class TestCreateUserInputDTO:
    def test_input_dto_creation(self):
        dto = CreateUserInputDTO(
            id=456,
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

        assert dto.id == 456
        assert dto.username == "testuser"
        assert dto.first_name == "John"
        assert dto.last_name == "Doe"

    def test_input_dto_with_none_values(self):
        dto = CreateUserInputDTO(
            id=789,
            username=None,
            first_name="Jane",
            last_name=None,
        )

        assert dto.id == 789
        assert dto.username is None
        assert dto.first_name == "Jane"
        assert dto.last_name is None


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
