"""
Unit tests for common/helpers/exceptions.py custom exceptions.
"""
import pytest
from common.helpers.exceptions import InputValidationError, APIException


class TestInputValidationError:
    """Test InputValidationError exception."""

    def test_input_validation_error_instantiation(self):
        """Test InputValidationError can be instantiated."""
        error = InputValidationError("Test error message")
        assert isinstance(error, Exception)
        assert isinstance(error, InputValidationError)

    def test_input_validation_error_message(self):
        """Test InputValidationError stores and returns message."""
        error_msg = "Invalid input provided"
        error = InputValidationError(error_msg)
        assert str(error) == error_msg

    def test_input_validation_error_can_be_raised(self):
        """Test InputValidationError can be raised and caught."""
        with pytest.raises(InputValidationError) as exc_info:
            raise InputValidationError("Test error")
        assert "Test error" in str(exc_info.value)

    def test_input_validation_error_with_empty_message(self):
        """Test InputValidationError with empty message."""
        error = InputValidationError("")
        assert str(error) == ""

    def test_input_validation_error_with_complex_message(self):
        """Test InputValidationError with complex message."""
        error_msg = "Multiple validation errors: field1 is required, field2 must be numeric"
        error = InputValidationError(error_msg)
        assert str(error) == error_msg


class TestAPIException:
    """Test APIException exception."""

    def test_api_exception_instantiation(self):
        """Test APIException can be instantiated."""
        error = APIException("API error occurred")
        assert isinstance(error, Exception)
        assert isinstance(error, APIException)

    def test_api_exception_message(self):
        """Test APIException stores and returns message."""
        error_msg = "Internal server error"
        error = APIException(error_msg)
        assert str(error) == error_msg

    def test_api_exception_can_be_raised(self):
        """Test APIException can be raised and caught."""
        with pytest.raises(APIException) as exc_info:
            raise APIException("API failure")
        assert "API failure" in str(exc_info.value)

    def test_api_exception_with_empty_message(self):
        """Test APIException with empty message."""
        error = APIException("")
        assert str(error) == ""

    def test_api_exception_with_detailed_message(self):
        """Test APIException with detailed error message."""
        error_msg = "Database connection failed: timeout after 30 seconds"
        error = APIException(error_msg)
        assert str(error) == error_msg

    def test_exceptions_are_distinct(self):
        """Test that InputValidationError and APIException are distinct."""
        validation_error = InputValidationError("Validation")
        api_error = APIException("API")

        assert not isinstance(validation_error, APIException)
        assert not isinstance(api_error, InputValidationError)
        assert isinstance(validation_error, Exception)
        assert isinstance(api_error, Exception)
