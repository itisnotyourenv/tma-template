from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.auth.tg import AuthTgInputDTO, AuthTgInteractor, AuthTgOutputDTO
from src.application.interfaces.auth import InitDataDTO
from src.domain.user import User
from src.domain.user.vo import Bio, FirstName, LastName, UserId, Username


class TestAuthTgInteractor:
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
    ) -> AuthTgInteractor:
        return AuthTgInteractor(
            user_repository=mock_user_repository,
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
            is_premium=False,
            start_param=None,
            photo_url="http://example.com/photo.jpg",
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

    async def test_auth_new_user_success(
        self,
        interactor,
        mock_user_repository,
        mock_auth_service,
        mock_transaction_manager,
        sample_auth_tg_input_dto,
        sample_init_data_dto,
    ):
        # prepare auth service mocks
        mock_auth_service.validate_init_data = Mock(return_value=sample_init_data_dto)
        jwt_token = "valid_jwt_token"
        mock_auth_service.create_access_token = Mock(return_value=jwt_token)
        # mock repository methods
        mock_user_repository.get_user = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(return_value=None)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_auth_tg_input_dto)

        assert isinstance(result, AuthTgOutputDTO)
        assert result.access_token == jwt_token

        mock_auth_service.validate_init_data.assert_called_once()
        mock_user_repository.get_user.assert_awaited_once()
        mock_user_repository.create_user.assert_awaited_once()
        mock_user_repository.update_user.assert_not_called()
        mock_transaction_manager.commit.assert_called_once()
        mock_auth_service.create_access_token.assert_called_once()

    async def test_auth_existed_user_success(
        self,
        interactor,
        mock_user_repository,
        mock_auth_service,
        mock_transaction_manager,
        sample_auth_tg_input_dto,
        sample_init_data_dto,
        sample_user,
    ):
        # prepare auth service mocks
        mock_auth_service.validate_init_data = Mock(return_value=sample_init_data_dto)
        jwt_token = "valid_jwt_token"
        mock_auth_service.create_access_token = Mock(return_value=jwt_token)

        # mock repository methods
        mock_user_repository.get_user = AsyncMock(return_value=sample_user)
        mock_user_repository.update_user = AsyncMock(return_value=None)
        mock_transaction_manager.commit = AsyncMock()

        result = await interactor(sample_auth_tg_input_dto)

        assert isinstance(result, AuthTgOutputDTO)
        assert result.access_token == jwt_token

        mock_auth_service.validate_init_data.assert_called_once()
        mock_user_repository.get_user.assert_awaited_once()
        mock_user_repository.update_user.assert_awaited_once()

        mock_transaction_manager.commit.assert_called_once()
        mock_auth_service.create_access_token.assert_called_once()
