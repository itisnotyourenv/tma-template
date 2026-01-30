import pytest

from src.domain.user.vo import Bio, FirstName, LastName, ReferralCount, UserId, Username


class TestUserId:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (1, 1),
            (123, 123),
            (999999, 999999),
        ],
    )
    def test_valid_user_id(self, value, expected):
        user_id = UserId(value)
        assert user_id.value == expected

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            ("123", "UserId value must be an int"),
            (12.5, "UserId value must be an int"),
            (None, "UserId value must be an int"),
            ([], "UserId value must be an int"),
        ],
    )
    def test_invalid_type(self, invalid_value, expected_error):
        with pytest.raises(TypeError, match=expected_error):
            UserId(invalid_value)

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            (-1, "UserId value must be a positive integer"),
            (0, "UserId value must be a positive integer"),
            (-999, "UserId value must be a positive integer"),
        ],
    )
    def test_invalid_values(self, invalid_value, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            UserId(invalid_value)

    def test_equality(self):
        user_id1 = UserId(123)
        user_id2 = UserId(123)
        user_id3 = UserId(456)

        assert user_id1 == user_id2
        assert user_id1 != user_id3

    def test_hash(self):
        user_id1 = UserId(123)
        user_id2 = UserId(123)

        assert hash(user_id1) == hash(user_id2)

    def test_str_representation(self):
        user_id = UserId(123)
        assert str(user_id) == "123"

    def test_repr(self):
        user_id = UserId(123)
        assert repr(user_id) == "UserId(123)"


class TestFirstName:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("John", "John"),
            ("A", "A"),
            ("A" * 64, "A" * 64),
            ("Jos�", "Jos�"),
            ("Mary-Jane", "Mary-Jane"),
        ],
    )
    def test_valid_first_name(self, value, expected):
        first_name = FirstName(value)
        assert first_name.value == expected

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            ("", "FirstName value must be between 1 and 64 characters long"),
            ("A" * 65, "FirstName value must be between 1 and 64 characters long"),
            ("A" * 100, "FirstName value must be between 1 and 64 characters long"),
        ],
    )
    def test_invalid_length(self, invalid_value, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            FirstName(invalid_value)

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            (123, "FirstName value must be a str"),
            (None, "FirstName value must be a str"),
            ([], "FirstName value must be a str"),
            (12.5, "FirstName value must be a str"),
        ],
    )
    def test_invalid_type(self, invalid_value, expected_error):
        with pytest.raises(TypeError, match=expected_error):
            FirstName(invalid_value)


class TestLastName:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("Doe", "Doe"),
            ("", ""),
            ("A" * 64, "A" * 64),
            ("Smith-Jones", "Smith-Jones"),
            ("O'Connor", "O'Connor"),
        ],
    )
    def test_valid_last_name(self, value, expected):
        last_name = LastName(value)
        assert last_name.value == expected

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            ("A" * 65, "LastName value must be between 0 and 64 characters long"),
            ("A" * 100, "LastName value must be between 0 and 64 characters long"),
        ],
    )
    def test_invalid_length(self, invalid_value, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            LastName(invalid_value)

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            (123, "LastName value must be a str"),
            (None, "LastName value must be a str"),
            ([], "LastName value must be a str"),
            (12.5, "LastName value must be a str"),
        ],
    )
    def test_invalid_type(self, invalid_value, expected_error):
        with pytest.raises(TypeError, match=expected_error):
            LastName(invalid_value)


class TestUsername:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("john_doe", "john_doe"),
            ("john", "john"),
            ("a" * 32, "a" * 32),
            ("user123", "user123"),
            ("test_user_name", "test_user_name"),
        ],
    )
    def test_valid_username(self, value, expected):
        username = Username(value)
        assert username.value == expected

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            ("abc", "Username value must be between 4 and 32 characters long"),
            ("a" * 33, "Username value must be between 4 and 32 characters long"),
            ("a" * 50, "Username value must be between 4 and 32 characters long"),
            ("", "Username value must be between 4 and 32 characters long"),
        ],
    )
    def test_invalid_length(self, invalid_value, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            Username(invalid_value)

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            (123, "Username value must be a str"),
            (None, "Username value must be a str"),
            ([], "Username value must be a str"),
            (12.5, "Username value must be a str"),
        ],
    )
    def test_invalid_type(self, invalid_value, expected_error):
        with pytest.raises(TypeError, match=expected_error):
            Username(invalid_value)


class TestBio:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("Software developer", "Software developer"),
            ("", ""),
            ("A" * 160, "A" * 160),
            ("D�veloppeur =h=�", "D�veloppeur =h=�"),
            ("Multi-line\nbio content", "Multi-line\nbio content"),
        ],
    )
    def test_valid_bio(self, value, expected):
        bio = Bio(value)
        assert bio.value == expected

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            ("A" * 161, "Bio value must be between 0 and 160 characters long"),
            ("A" * 200, "Bio value must be between 0 and 160 characters long"),
        ],
    )
    def test_invalid_length(self, invalid_value, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            Bio(invalid_value)

    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            (123, "Bio value must be a str"),
            (None, "Bio value must be a str"),
            ([], "Bio value must be a str"),
            (12.5, "Bio value must be a str"),
        ],
    )
    def test_invalid_type(self, invalid_value, expected_error):
        with pytest.raises(TypeError, match=expected_error):
            Bio(invalid_value)


class TestReferralCount:
    @pytest.mark.parametrize("value,expected", [(0, 0), (1, 1), (100, 100)])
    def test_valid_referral_count(self, value, expected):
        rc = ReferralCount(value)
        assert rc.value == expected

    def test_negative_value_raises(self):
        with pytest.raises(ValueError):
            ReferralCount(-1)

    def test_invalid_type_raises(self):
        with pytest.raises((TypeError, ValueError)):
            ReferralCount("not a number")

    def test_equality(self):
        rc1 = ReferralCount(5)
        rc2 = ReferralCount(5)
        rc3 = ReferralCount(10)

        assert rc1 == rc2
        assert rc1 != rc3

    def test_repr(self):
        rc = ReferralCount(5)
        assert repr(rc) == "ReferralCount(5)"


class TestValueObjectsEquality:
    def test_different_types_not_equal(self):
        user_id = UserId(123)
        first_name = FirstName("123")

        assert user_id != first_name

    def test_same_values_different_classes(self):
        first_name = FirstName("test")
        last_name = LastName("test")

        assert first_name != last_name
