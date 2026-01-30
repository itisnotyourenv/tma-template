import pytest

from src.domain.user.services.referral import find_referrer_id, generate_referral_code


class TestGenerateReferralCode:
    def test_returns_8_character_string(self):
        code = generate_referral_code(123456789)
        assert len(code) == 8
        assert isinstance(code, str)

    def test_deterministic_same_input_same_output(self):
        code1 = generate_referral_code(123456789)
        code2 = generate_referral_code(123456789)
        assert code1 == code2

    def test_different_inputs_different_outputs(self):
        code1 = generate_referral_code(123)
        code2 = generate_referral_code(456)
        assert code1 != code2

    def test_contains_only_hex_characters(self):
        code = generate_referral_code(999)
        assert all(c in "0123456789abcdef" for c in code)

    @pytest.mark.parametrize("user_id", [1, 100, 999999999, 9223372036854775807])
    def test_handles_various_user_ids(self, user_id):
        code = generate_referral_code(user_id)
        assert len(code) == 8


class TestFindReferrerId:
    def test_finds_existing_user(self):
        user_id = 123456789
        code = generate_referral_code(user_id)
        found = find_referrer_id(code, [111, 222, user_id, 333])
        assert found == user_id

    def test_returns_none_for_unknown_code(self):
        found = find_referrer_id("abcd1234", [111, 222, 333])
        assert found is None

    def test_returns_none_for_empty_list(self):
        found = find_referrer_id("abcd1234", [])
        assert found is None
