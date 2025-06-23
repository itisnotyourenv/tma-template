import pytest
from src.domain.user.vo import UserId, FirstName, LastName, Username, Bio


class TestUserId:
    def test_valid_user_id(self):
        user_id = UserId(123)
        assert user_id.value == 123

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="UserId value must be an int"):
            UserId("123")

    def test_negative_value(self):
        with pytest.raises(ValueError, match="UserId value must be a positive integer"):
            UserId(-1)

    def test_zero_value(self):
        with pytest.raises(ValueError, match="UserId value must be a positive integer"):
            UserId(0)

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
    def test_valid_first_name(self):
        first_name = FirstName("John")
        assert first_name.value == "John"

    def test_minimum_length(self):
        first_name = FirstName("A")
        assert first_name.value == "A"

    def test_maximum_length(self):
        long_name = "A" * 64
        first_name = FirstName(long_name)
        assert first_name.value == long_name

    def test_empty_string(self):
        with pytest.raises(ValueError, match="FirstName value must be between 1 and 64 characters long"):
            FirstName("")

    def test_too_long(self):
        long_name = "A" * 65
        with pytest.raises(ValueError, match="FirstName value must be between 1 and 64 characters long"):
            FirstName(long_name)

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="FirstName value must be a str"):
            FirstName(123)

    def test_unicode_characters(self):
        first_name = FirstName("Jos�")
        assert first_name.value == "Jos�"


class TestLastName:
    def test_valid_last_name(self):
        last_name = LastName("Doe")
        assert last_name.value == "Doe"

    def test_minimum_length_zero(self):
        last_name = LastName("")
        assert last_name.value == ""

    def test_maximum_length(self):
        long_name = "A" * 64
        last_name = LastName(long_name)
        assert last_name.value == long_name

    def test_too_long(self):
        long_name = "A" * 65
        with pytest.raises(ValueError, match="LastName value must be between 0 and 64 characters long"):
            LastName(long_name)

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="LastName value must be a str"):
            LastName(123)


class TestUsername:
    def test_valid_username(self):
        username = Username("john_doe")
        assert username.value == "john_doe"

    def test_minimum_length(self):
        username = Username("john")
        assert username.value == "john"

    def test_maximum_length(self):
        long_username = "a" * 32
        username = Username(long_username)
        assert username.value == long_username

    def test_too_short(self):
        with pytest.raises(ValueError, match="Username value must be between 4 and 32 characters long"):
            Username("abc")

    def test_too_long(self):
        long_username = "a" * 33
        with pytest.raises(ValueError, match="Username value must be between 4 and 32 characters long"):
            Username(long_username)

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="Username value must be a str"):
            Username(123)


class TestBio:
    def test_valid_bio(self):
        bio = Bio("Software developer")
        assert bio.value == "Software developer"

    def test_empty_bio(self):
        bio = Bio("")
        assert bio.value == ""

    def test_maximum_length(self):
        long_bio = "A" * 160
        bio = Bio(long_bio)
        assert bio.value == long_bio

    def test_too_long(self):
        long_bio = "A" * 161
        with pytest.raises(ValueError, match="Bio value must be between 0 and 160 characters long"):
            Bio(long_bio)

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="Bio value must be a str"):
            Bio(123)

    def test_unicode_characters(self):
        bio = Bio("D�veloppeur =h=�")
        assert bio.value == "D�veloppeur =h=�"


class TestValueObjectsEquality:
    def test_different_types_not_equal(self):
        user_id = UserId(123)
        first_name = FirstName("123")
        
        assert user_id != first_name

    def test_same_values_different_classes(self):
        first_name = FirstName("test")
        last_name = LastName("test")
        
        assert first_name != last_name