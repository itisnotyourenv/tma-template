from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.auth.tg import AuthTgInputDTO, AuthTgInteractor, AuthTgOutputDTO
from src.application.interfaces.auth import InitDataDTO
from src.application.user.service import UserService
from src.domain.user import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username


class TestAuthTgInteractor:
    @pytest.fixture
    def mock_user_service(self):
        return Mock(spec=UserService)

    @pytest.fixture
    def mock_transaction_manager(self):
        return Mock()

    @pytest.fixture
    def mock_auth_service(self):
        return Mock()

    @pytest.fixture
    def interactor(
        self,
        mock_user_service,
        mock_auth_service,
        mock_transaction_manager,
    ) -> AuthTgInteractor:
        return AuthTgInteractor(
            user_service=mock_user_service,
            auth_service=mock_auth_service,
            transaction_manager=mock_transaction_manager,
        )

    @pytest.fixture
    def sample_init_data_dto(self) -> InitDataDTO:
        return InitDataDTO(
            user_id=456,
            username="testuser",
            first_name="Test",
            last_name="User",
            start_param=None,
            ui_language_code="en",
        )

    @pytest.fixture
    def sample_auth_tg_input_dto(self) -> AuthTgInputDTO:
        return AuthTgInputDTO(init_data="valid_init_data_string")

    @pytest.fixture
    def sample_user(self) -> User:
        now = datetime.now(UTC)
        return User(
            id=UserId(456),
            username=Username("username"),
            first_name=FirstName("Johhn"),
            last_name=LastName("Anderson"),
            bio=Bio("Hello, I'm a test user."),
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

    async def test_auth_user_success(
        self,
        interactor,
        mock_user_service,
        mock_auth_service,
        mock_transaction_manager,
        sample_auth_tg_input_dto,
        sample_init_data_dto,
        sample_user,
    ):
        mock_auth_service.validate_init_data = Mock(return_value=sample_init_data_dto)
        jwt_token = "valid_jwt_token"
        mock_auth_service.create_access_token = Mock(return_value=jwt_token)
        mock_user_service.upsert_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_auth_tg_input_dto)

        assert isinstance(result, AuthTgOutputDTO)
        assert result.access_token == jwt_token

        mock_auth_service.validate_init_data.assert_called_once_with(
            sample_auth_tg_input_dto.init_data
        )
        mock_user_service.upsert_user.assert_awaited_once()
        mock_transaction_manager.commit.assert_called_once()
        mock_auth_service.create_access_token.assert_called_once_with(
            sample_init_data_dto.user_id
        )

    async def test_auth_service_validate_exception_propagated(
        self,
        interactor,
        mock_user_service,
        mock_auth_service,
        mock_transaction_manager,
        sample_auth_tg_input_dto,
    ):
        mock_auth_service.validate_init_data = Mock(
            side_effect=Exception("Invalid init data")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_auth_tg_input_dto)

        assert "Invalid init data" in str(exc_info.value)
        mock_user_service.upsert_user.assert_not_called()
        mock_transaction_manager.commit.assert_not_called()

    async def test_user_service_exception_propagated(
        self,
        interactor,
        mock_user_service,
        mock_auth_service,
        mock_transaction_manager,
        sample_auth_tg_input_dto,
        sample_init_data_dto,
    ):
        mock_auth_service.validate_init_data = Mock(return_value=sample_init_data_dto)
        mock_user_service.upsert_user = AsyncMock(
            side_effect=Exception("Database error")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_auth_tg_input_dto)

        assert "Database error" in str(exc_info.value)
        mock_transaction_manager.commit.assert_not_called()

    async def test_transaction_commit_exception_propagated(
        self,
        interactor,
        mock_user_service,
        mock_auth_service,
        mock_transaction_manager,
        sample_auth_tg_input_dto,
        sample_init_data_dto,
        sample_user,
    ):
        mock_auth_service.validate_init_data = Mock(return_value=sample_init_data_dto)
        mock_user_service.upsert_user = AsyncMock(return_value=sample_user)
        mock_transaction_manager.commit = AsyncMock(
            side_effect=Exception("Commit failed")
        )

        with pytest.raises(Exception) as exc_info:
            await interactor(sample_auth_tg_input_dto)

        assert "Commit failed" in str(exc_info.value)
        mock_auth_service.create_access_token.assert_not_called()
