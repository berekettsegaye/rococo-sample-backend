"""
Unit tests for common/helpers/exceptions.py
"""
import pytest
from common.helpers.exceptions import InputValidationError, APIException


class TestInputValidationError:
    """Tests for InputValidationError exception."""

    def test_input_validation_error_can_be_raised(self):
        """Test that InputValidationError can be raised and caught."""
        with pytest.raises(InputValidationError):
            raise InputValidationError("Validation failed")

    def test_input_validation_error_message_preserved(self):
        """Test that error message is preserved when raised."""
        error_message = "Invalid email format"
        with pytest.raises(InputValidationError) as exc_info:
            raise InputValidationError(error_message)

        assert str(exc_info.value) == error_message


class TestAPIException:
    """Tests for APIException exception."""

    def test_api_exception_can_be_raised(self):
        """Test that APIException can be raised and caught."""
        with pytest.raises(APIException):
            raise APIException("API error occurred")

    def test_api_exception_message_preserved(self):
        """Test that error message is preserved when raised."""
        error_message = "Resource not found"
        with pytest.raises(APIException) as exc_info:
            raise APIException(error_message)

        assert str(exc_info.value) == error_message
