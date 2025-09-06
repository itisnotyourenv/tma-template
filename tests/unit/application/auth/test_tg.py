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
        return User(
            id=UserId(456),
            username=Username("username"),
            first_name=FirstName("Johhn"),
            last_name=LastName("Anderson"),
            bio=Bio("Hello, I'm a test user."),
        )

    #
    # @pytest.fixture
    # def answer_input(self):
    #     return AnswerInputDTO(
    #         question_id="123e4567-e89b-12d3-a456-426614174000",
    #         user_id=UserId(456),
    #         text="Python is my favorite programming language",
    #     )

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


#
#     async def test_question_not_found_error(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         answer_input,
#     ):
#         mock_question_repository.get_question_by_uuid = AsyncMock(return_value=None)
#
#         with pytest.raises(QuestionNotFoundError) as exc_info:
#             await interactor(answer_input)
#
#         assert "123e4567-e89b-12d3-a456-426614174000" in str(exc_info.value)
#         mock_question_repository.get_question_by_uuid.assert_called_once()
#         mock_answer_repository.create_answer.assert_not_called()
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_unauthorized_access_error(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_question,
#     ):
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#
#         unauthorized_input = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(999),  # Different user ID (not the receiver)
#             text="This should fail",
#         )
#
#         with pytest.raises(UnauthorizedAccessError) as exc_info:
#             await interactor(unauthorized_input)
#
#         assert "User 999 is not authorized" in str(exc_info.value)
#         assert "123e4567-e89b-12d3-a456-426614174000" in str(exc_info.value)
#         mock_question_repository.get_question_by_uuid.assert_called_once()
#         mock_answer_repository.create_answer.assert_not_called()
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_invalid_uuid_format(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#     ):
#         invalid_input = AnswerInputDTO(
#             question_id="invalid-uuid-format",
#             user_id=UserId(456),
#             text="Valid answer text",
#         )
#
#         with pytest.raises(ValueError) as exc_info:
#             await interactor(invalid_input)
#
#         assert "UUID value must be a valid UUID format" in str(exc_info.value)
#         mock_question_repository.get_question_by_uuid.assert_not_called()
#         mock_answer_repository.create_answer.assert_not_called()
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_invalid_answer_text_too_short(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#     ):
#         invalid_input = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(456),
#             text="",  # Empty text (below minimum length)
#         )
#
#         with pytest.raises(ValueError) as exc_info:
#             await interactor(invalid_input)
#
#         assert "must be between 1 and 2048 characters" in str(exc_info.value)
#         mock_question_repository.get_question_by_uuid.assert_not_called()
#         mock_answer_repository.create_answer.assert_not_called()
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_invalid_answer_text_too_long(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#     ):
#         long_text = "a" * 2049  # Exceeds maximum length of 2048
#         invalid_input = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(456),
#             text=long_text,
#         )
#
#         with pytest.raises(ValueError) as exc_info:
#             await interactor(invalid_input)
#
#         assert "value must be between 1 and 2048" in str(exc_info.value)
#         mock_question_repository.get_question_by_uuid.assert_not_called()
#         mock_answer_repository.create_answer.assert_not_called()
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_valid_answer_text_boundaries(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_question,
#         sample_answer,
#     ):
#         # Test minimum length (1 character)
#         min_input = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(456),
#             text="A",
#         )
#
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#         mock_question_repository.update_question = AsyncMock()
#         mock_answer_repository.create_answer = AsyncMock(return_value=sample_answer)
#         mock_transaction_manager.commit = AsyncMock()
#
#         result = await interactor(min_input)
#         assert isinstance(result, AnswerOutputDTO)
#
#         # Reset mocks
#         mock_question_repository.get_question_by_uuid.reset_mock()
#         mock_answer_repository.create_answer.reset_mock()
#         mock_transaction_manager.commit.reset_mock()
#
#         # Test maximum length (2048 characters)
#         max_text = "a" * 2048
#         max_input = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(456),
#             text=max_text,
#         )
#
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#         mock_answer_repository.create_answer = AsyncMock(return_value=sample_answer)
#         mock_transaction_manager.commit = AsyncMock()
#
#         result = await interactor(max_input)
#         assert isinstance(result, AnswerOutputDTO)
#
#     async def test_repository_exception_propagated(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         answer_input,
#     ):
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             side_effect=Exception("Database connection failed")
#         )
#
#         with pytest.raises(Exception) as exc_info:
#             await interactor(answer_input)
#
#         assert "Database connection failed" in str(exc_info.value)
#         mock_answer_repository.create_answer.assert_not_called()
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_answer_repository_exception_propagated(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_question,
#         answer_input,
#     ):
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#         mock_answer_repository.create_answer = AsyncMock(
#             side_effect=Exception("Failed to create answer")
#         )
#
#         with pytest.raises(Exception) as exc_info:
#             await interactor(answer_input)
#
#         assert "Failed to create answer" in str(exc_info.value)
#         mock_transaction_manager.commit.assert_not_called()
#
#     async def test_transaction_manager_exception_propagated(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_question,
#         sample_answer,
#         answer_input,
#     ):
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#         mock_question_repository.update_question = AsyncMock()
#
#         mock_answer_repository.create_answer = AsyncMock(return_value=sample_answer)
#         mock_transaction_manager.commit = AsyncMock(
#             side_effect=Exception("Transaction commit failed")
#         )
#
#         with pytest.raises(Exception) as exc_info:
#             await interactor(answer_input)
#
#         assert "Transaction commit failed" in str(exc_info.value)
#
#     @pytest.mark.parametrize("user_id_value", [1, 999999999, 123])
#     async def test_various_user_ids(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_answer,
#         user_id_value,
#     ):
#         question = Question(
#             uuid=UUIDValueObject("123e4567-e89b-12d3-a456-426614174000"),
#             text=QuestionText("Test question"),
#             sender_id=UserId(100),
#             receiver_id=UserId(user_id_value),
#             likes_count=0,
#             is_read=False,
#             is_answered=False,
#             is_archived=False,
#             is_public=True,
#             created_at=CreatedAt.now(),
#             updated_at=UpdatedAt.now(),
#         )
#
#         input_dto = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(user_id_value),
#             text="Test answer",
#         )
#
#         mock_question_repository.get_question_by_uuid = AsyncMock(return_value=question)
#         mock_question_repository.update_question = AsyncMock()
#         mock_answer_repository.create_answer = AsyncMock(return_value=sample_answer)
#         mock_transaction_manager.commit = AsyncMock()
#
#         result = await interactor(input_dto)
#
#         assert isinstance(result, AnswerOutputDTO)
#         mock_answer_repository.create_answer.assert_called_once()
#
#     async def test_answer_uuid_generation(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_question,
#         answer_input,
#     ):
#         """Test that answer UUID is properly generated and matches question UUID."""
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#         mock_question_repository.update_question = AsyncMock()
#
#         # Create answer with same UUID as question (as per implementation)
#         answer_with_question_uuid = Answer(
#             uuid=sample_question.uuid,  # Uses question's UUID
#             text=AnswerText("Test answer"),
#             question_id=QuestionId(sample_question.uuid.value),
#             sender_id=UserId(456),
#             created_at=CreatedAt.now(),
#             updated_at=UpdatedAt.now(),
#         )
#
#         mock_answer_repository.create_answer = AsyncMock(
#             return_value=answer_with_question_uuid
#         )
#         mock_transaction_manager.commit = AsyncMock()
#
#         result = await interactor(answer_input)
#
#         assert result.uuid == sample_question.uuid.value
#         create_call_args = mock_answer_repository.create_answer.call_args[1]["answer"]
#         assert create_call_args.uuid == sample_question.uuid
#
#     async def test_answer_timestamps_set(
#         self,
#         interactor,
#         mock_question_repository,
#         mock_answer_repository,
#         mock_transaction_manager,
#         sample_question,
#         sample_answer,
#         answer_input,
#     ):
#         """Test that created_at and updated_at timestamps are properly set."""
#         mock_question_repository.get_question_by_uuid = AsyncMock(
#             return_value=sample_question
#         )
#         mock_question_repository.update_question = AsyncMock()
#         mock_answer_repository.create_answer = AsyncMock(return_value=sample_answer)
#         mock_transaction_manager.commit = AsyncMock()
#
#         await interactor(answer_input)
#
#         create_call_args = mock_answer_repository.create_answer.call_args[1]["answer"]
#         assert create_call_args.created_at is not None
#         assert create_call_args.updated_at is not None
#         assert isinstance(create_call_args.created_at, CreatedAt)
#         assert isinstance(create_call_args.updated_at, UpdatedAt)
#
#
# class TestAnswerInputDTO:
#     def test_input_dto_creation(self):
#         dto = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(456),
#             text="Test answer",
#         )
#
#         assert dto.question_id == "123e4567-e89b-12d3-a456-426614174000"
#         assert dto.user_id == UserId(456)
#         assert dto.text == "Test answer"
#
#     def test_input_dto_immutability(self):
#         dto = AnswerInputDTO(
#             question_id="123e4567-e89b-12d3-a456-426614174000",
#             user_id=UserId(456),
#             text="Test answer",
#         )
#
#         # FrozenInstanceError for dataclass(frozen=True)
#         with pytest.raises(Exception):
#             dto.text = "Modified answer"
#
#
# class TestAnswerOutputDTO:
#     def test_output_dto_creation(self):
#         dto = AnswerOutputDTO(
#             uuid="987f6543-e21c-34d5-b678-539725285111",
#             text="Test answer",
#         )
#
#         assert dto.uuid == "987f6543-e21c-34d5-b678-539725285111"
#         assert dto.text == "Test answer"
#
#     def test_output_dto_immutability(self):
#         dto = AnswerOutputDTO(
#             uuid="987f6543-e21c-34d5-b678-539725285111",
#             text="Test answer",
#         )
#
#         with pytest.raises(Exception):
#             dto.text = "Modified answer"
