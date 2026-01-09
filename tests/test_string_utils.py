"""
Unit tests for common/helpers/string_utils.py
"""
import pytest
import base64
from datetime import datetime, date, time
from decimal import Decimal


class TestNormalUrlSafeB64Decode:
    """Tests for normal_url_safe_b64_decode function."""

    def test_decode_valid_string(self):
        """Test decoding a valid base64 encoded string."""
        from common.helpers.string_utils import normal_url_safe_b64_decode, normal_url_safe_b64_encode

        original = "Hello, World!"
        encoded = normal_url_safe_b64_encode(original)
        decoded = normal_url_safe_b64_decode(encoded)

        assert decoded == original

    def test_decode_empty_string(self):
        """Test decoding empty string."""
        from common.helpers.string_utils import normal_url_safe_b64_decode

        encoded = base64.urlsafe_b64encode(b'').decode('utf-8')
        result = normal_url_safe_b64_decode(encoded)

        assert result == ""

    def test_decode_special_characters(self):
        """Test decoding string with special characters."""
        from common.helpers.string_utils import normal_url_safe_b64_decode, normal_url_safe_b64_encode

        original = "test@example.com!#$%"
        encoded = normal_url_safe_b64_encode(original)
        decoded = normal_url_safe_b64_decode(encoded)

        assert decoded == original


class TestNormalUrlSafeB64Encode:
    """Tests for normal_url_safe_b64_encode function."""

    def test_encode_valid_string(self):
        """Test encoding a valid string."""
        from common.helpers.string_utils import normal_url_safe_b64_encode

        original = "Hello, World!"
        encoded = normal_url_safe_b64_encode(original)

        # Verify it's a valid base64 string
        assert isinstance(encoded, str)
        # Verify it can be decoded back
        decoded = base64.urlsafe_b64decode(encoded.encode('utf-8')).decode('utf-8')
        assert decoded == original

    def test_encode_empty_string(self):
        """Test encoding empty string."""
        from common.helpers.string_utils import normal_url_safe_b64_encode

        result = normal_url_safe_b64_encode("")
        assert result == ""

    def test_encode_unicode_string(self):
        """Test encoding unicode characters."""
        from common.helpers.string_utils import normal_url_safe_b64_encode, normal_url_safe_b64_decode

        original = "Hello 世界 🌍"
        encoded = normal_url_safe_b64_encode(original)
        decoded = normal_url_safe_b64_decode(encoded)

        assert decoded == original


class TestIsProtectedType:
    """Tests for is_protected_type function."""

    def test_none_is_protected(self):
        """Test that None is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(None) is True

    def test_int_is_protected(self):
        """Test that int is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(42) is True
        assert is_protected_type(0) is True

    def test_float_is_protected(self):
        """Test that float is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(3.14) is True

    def test_decimal_is_protected(self):
        """Test that Decimal is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(Decimal('10.5')) is True

    def test_datetime_is_protected(self):
        """Test that datetime is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(datetime.now()) is True

    def test_date_is_protected(self):
        """Test that date is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(date.today()) is True

    def test_time_is_protected(self):
        """Test that time is a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type(time()) is True

    def test_string_not_protected(self):
        """Test that string is not a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type("hello") is False

    def test_list_not_protected(self):
        """Test that list is not a protected type."""
        from common.helpers.string_utils import is_protected_type

        assert is_protected_type([1, 2, 3]) is False


class TestUrlsafeBase64Encode:
    """Tests for urlsafe_base64_encode function."""

    def test_encode_bytes(self):
        """Test encoding bytes."""
        from common.helpers.string_utils import urlsafe_base64_encode

        data = b"Hello, World!"
        encoded = urlsafe_base64_encode(data)

        assert isinstance(encoded, str)
        assert '=' not in encoded  # Padding should be stripped

    def test_encode_empty_bytes(self):
        """Test encoding empty bytes."""
        from common.helpers.string_utils import urlsafe_base64_encode

        result = urlsafe_base64_encode(b"")
        assert result == ""

    def test_encode_strips_padding(self):
        """Test that padding is stripped from encoded output."""
        from common.helpers.string_utils import urlsafe_base64_encode

        # This string when encoded will have padding
        data = b"test"
        encoded = urlsafe_base64_encode(data)

        # Verify no padding characters
        assert '=' not in encoded
        assert '\n' not in encoded


class TestUrlsafeBase64Decode:
    """Tests for urlsafe_base64_decode function."""

    def test_decode_valid_string(self):
        """Test decoding a valid base64 string."""
        from common.helpers.string_utils import urlsafe_base64_encode, urlsafe_base64_decode

        original = b"Hello, World!"
        encoded = urlsafe_base64_encode(original)
        decoded = urlsafe_base64_decode(encoded)

        assert decoded == original

    def test_decode_without_padding(self):
        """Test decoding string without padding."""
        from common.helpers.string_utils import urlsafe_base64_decode

        # Create a base64 string without padding
        encoded = "dGVzdA"  # "test" in base64 without padding
        decoded = urlsafe_base64_decode(encoded)

        assert decoded == b"test"

    def test_decode_special_char_string(self):
        """Test decoding string with special characters returns empty bytes."""
        from common.helpers.string_utils import urlsafe_base64_decode

        # Characters like @#$% may decode to empty or minimal bytes, not raise error
        result = urlsafe_base64_decode("@#$%")
        assert isinstance(result, bytes)

    def test_decode_empty_string(self):
        """Test decoding empty string."""
        from common.helpers.string_utils import urlsafe_base64_decode

        result = urlsafe_base64_decode("")
        assert result == b""


class TestForceStr:
    """Tests for force_str function."""

    def test_string_remains_string(self):
        """Test that string input returns as-is."""
        from common.helpers.string_utils import force_str

        result = force_str("hello")
        assert result == "hello"

    def test_bytes_to_string(self):
        """Test converting bytes to string."""
        from common.helpers.string_utils import force_str

        result = force_str(b"hello")
        assert result == "hello"

    def test_bytes_with_encoding(self):
        """Test converting bytes with specific encoding."""
        from common.helpers.string_utils import force_str

        data = "hello".encode('utf-8')
        result = force_str(data, encoding='utf-8')
        assert result == "hello"

    def test_int_to_string(self):
        """Test converting int to string."""
        from common.helpers.string_utils import force_str

        result = force_str(42)
        assert result == "42"

    def test_protected_type_with_strings_only(self):
        """Test that protected types are preserved with strings_only=True."""
        from common.helpers.string_utils import force_str

        result = force_str(42, strings_only=True)
        assert result == 42

        result = force_str(None, strings_only=True)
        assert result is None

    def test_list_to_string(self):
        """Test converting list to string."""
        from common.helpers.string_utils import force_str

        result = force_str([1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_none_to_string(self):
        """Test converting None to string."""
        from common.helpers.string_utils import force_str

        result = force_str(None)
        assert result == "None"


class TestForceBytes:
    """Tests for force_bytes function."""

    def test_bytes_remains_bytes(self):
        """Test that bytes input returns as-is."""
        from common.helpers.string_utils import force_bytes

        data = b"hello"
        result = force_bytes(data)
        assert result == data

    def test_string_to_bytes(self):
        """Test converting string to bytes."""
        from common.helpers.string_utils import force_bytes

        result = force_bytes("hello")
        assert result == b"hello"

    def test_string_with_encoding(self):
        """Test converting string with specific encoding."""
        from common.helpers.string_utils import force_bytes

        result = force_bytes("hello", encoding='utf-8')
        assert result == b"hello"

    def test_bytes_with_different_encoding(self):
        """Test converting bytes from one encoding to another."""
        from common.helpers.string_utils import force_bytes

        data = "hello".encode('utf-8')
        result = force_bytes(data, encoding='utf-8')
        assert result == b"hello"

    def test_int_to_bytes(self):
        """Test converting int to bytes."""
        from common.helpers.string_utils import force_bytes

        result = force_bytes(42)
        assert result == b"42"

    def test_protected_type_with_strings_only(self):
        """Test that protected types are preserved with strings_only=True."""
        from common.helpers.string_utils import force_bytes

        result = force_bytes(42, strings_only=True)
        assert result == 42

    def test_memoryview_to_bytes(self):
        """Test converting memoryview to bytes."""
        from common.helpers.string_utils import force_bytes

        data = memoryview(b"hello")
        result = force_bytes(data)
        assert result == b"hello"

    def test_list_to_bytes(self):
        """Test converting list to bytes."""
        from common.helpers.string_utils import force_bytes

        result = force_bytes([1, 2, 3])
        assert result == b"[1, 2, 3]"
