import pytest

from src.domain.user.services.referral import decode_referral, encode_referral


class TestReferralEncoding:
    def test_encode_decode_roundtrip(self) -> None:
        user_id = 123456789
        secret_key = "test-secret-key"

        code = encode_referral(user_id, secret_key)
        decoded = decode_referral(code, secret_key)

        assert decoded == user_id

    def test_encode_produces_url_safe_string(self) -> None:
        user_id = 987654321
        secret_key = "my-secret"

        code = encode_referral(user_id, secret_key)

        assert all(c.isalnum() or c in "-_" for c in code)

    def test_decode_with_wrong_key_returns_different_id(self) -> None:
        user_id = 123456789
        code = encode_referral(user_id, "correct-key")

        decoded = decode_referral(code, "wrong-key")

        assert decoded != user_id

    def test_decode_invalid_code_returns_none(self) -> None:
        result = decode_referral("invalid!", "any-key")

        assert result is None

    def test_different_users_get_different_codes(self) -> None:
        secret = "shared-secret"

        code1 = encode_referral(111, secret)
        code2 = encode_referral(222, secret)

        assert code1 != code2

    @pytest.mark.parametrize("user_id", [1, 100, 999999999, 9223372036854775807])
    def test_handles_various_user_ids(self, user_id: int) -> None:
        secret = "test-secret"
        code = encode_referral(user_id, secret)
        decoded = decode_referral(code, secret)
        assert decoded == user_id
