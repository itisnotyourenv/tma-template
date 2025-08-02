from datetime import UTC, datetime, timedelta

from aiogram.utils.web_app import safe_parse_webapp_init_data
from jose.jwt import encode

from src.application.common.exceptions import ValidationError
from src.application.interfaces.auth import AuthService, InitDataDTO
from src.infrastructure.config import Config


class AuthServiceImpl(AuthService):
    def __init__(self, config: Config) -> None:
        self.config = config

    def validate_init_data(self, init_data: str) -> InitDataDTO:
        # todo - cover with tests
        try:
            parsed_data = safe_parse_webapp_init_data(self.config.telegram.bot_token, init_data)
        except ValueError as e:
            error_msg = f"Invalid init data '{init_data}'"
            raise ValidationError(message=error_msg)

        if parsed_data.user is None or parsed_data.user.photo_url is None:
            error_msg = f"Invalid init data '{init_data}'"
            raise ValidationError(message=error_msg)

        return InitDataDTO(
            user_id=parsed_data.user.id,
            username=parsed_data.user.username,
            first_name=parsed_data.user.first_name,
            last_name=parsed_data.user.last_name,
            is_premium=parsed_data.user.is_premium or False,
            start_param=parsed_data.start_param,
            photo_url=parsed_data.user.photo_url,
            ui_language_code=parsed_data.user.language_code,
        )

    def create_access_token(self, user_id: int) -> str:
        # todo - cover with tests
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(minutes=self.config.auth.access_token_expire_minutes),
        }
        encoded_jwt = encode(
            to_encode,
            self.config.auth.secret_key,
            algorithm=self.config.auth.algorithm,
            headers={"kid": "main"},
        )
        return encoded_jwt
