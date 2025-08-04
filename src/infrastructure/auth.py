from datetime import UTC, datetime, timedelta

from aiogram.utils.web_app import safe_parse_webapp_init_data
from jose import ExpiredSignatureError, JWTError
from jose.jwt import encode, decode

from src.application.auth.exceptions import InvalidInitDataError
from src.application.common.exceptions import ValidationError
from src.application.interfaces.auth import AuthService, InitDataDTO
from src.infrastructure.config import Config


class AuthServiceImpl(AuthService):
    def __init__(self, config: Config) -> None:
        self.config = config

    def validate_init_data(self, init_data: str) -> InitDataDTO:
        # todo - cover with tests
        try:
            parsed_data = safe_parse_webapp_init_data(
                self.config.telegram.bot_token, init_data
            )
        except ValueError:
            error_msg = f"Invalid init data '{init_data}'"
            raise InvalidInitDataError(message=error_msg)

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
            ui_language_code=parsed_data.user.language_code
            if parsed_data.user.language_code
            else None,
        )

    def create_access_token(self, user_id: int) -> str:
        # todo - cover with tests
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now(UTC)
            + timedelta(minutes=self.config.auth.access_token_expire_minutes),
        }
        encoded_jwt = encode(
            to_encode,
            self.config.auth.secret_key,
            algorithm=self.config.auth.algorithm,
            headers={"kid": "main"},
        )
        return encoded_jwt

    def validate_access_token(self, token: str) -> int:
        """Validate JWT token and return user_id if valid."""
        try:
            payload = decode(
                token,
                self.config.auth.secret_key,
                algorithms=[self.config.auth.algorithm],
            )
            user_id_str = payload.get("sub")
            if user_id_str is None:
                raise ValidationError("Token missing subject")

            return int(user_id_str)
        except ExpiredSignatureError:
            raise ValidationError("Token has expired")
        except JWTError:
            raise ValidationError("Invalid token")
        except (ValueError, TypeError):
            raise ValidationError("Invalid user ID in token")
