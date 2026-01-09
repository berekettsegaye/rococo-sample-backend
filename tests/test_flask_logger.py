"""
Unit tests for flask/logger.py
"""
import pytest
import logging
import sys
from unittest.mock import MagicMock, patch, Mock
from flask import Flask


class TestGetLogLevel:
    """Tests for _get_log_level function."""

    @patch('logger.config')
    def test_get_log_level_non_production(self, mock_config):
        """Test that non-production returns DEBUG level."""
        from logger import _get_log_level

        mock_config.APP_ENV = 'development'
        mock_config.LOGLEVEL = 'INFO'

        result = _get_log_level()

        assert result == logging.DEBUG

    @patch('logger.config')
    def test_get_log_level_production_info(self, mock_config):
        """Test that production returns configured level."""
        from logger import _get_log_level

        mock_config.APP_ENV = 'production'
        mock_config.LOGLEVEL = 'INFO'

        result = _get_log_level()

        assert result == logging.INFO

    @patch('logger.config')
    def test_get_log_level_production_warning(self, mock_config):
        """Test that production returns WARNING level."""
        from logger import _get_log_level

        mock_config.APP_ENV = 'production'
        mock_config.LOGLEVEL = 'WARNING'

        result = _get_log_level()

        assert result == logging.WARNING

    @patch('logger.config')
    def test_get_log_level_production_error(self, mock_config):
        """Test that production returns ERROR level."""
        from logger import _get_log_level

        mock_config.APP_ENV = 'production'
        mock_config.LOGLEVEL = 'ERROR'

        result = _get_log_level()

        assert result == logging.ERROR


class TestGetFormatter:
    """Tests for _get_formatter function."""

    def test_get_formatter_returns_formatter(self):
        """Test that _get_formatter returns a logging.Formatter."""
        from logger import _get_formatter

        result = _get_formatter()

        assert isinstance(result, logging.Formatter)

    def test_get_formatter_format_string(self):
        """Test that formatter has correct format string."""
        from logger import _get_formatter

        formatter = _get_formatter()

        # Test formatting a log record
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)

        assert 'INFO' in formatted
        assert 'Test message' in formatted


class TestRollbarExceptHook:
    """Tests for rollbar_except_hook function."""

    @patch('logger.rollbar.report_exc_info')
    @patch('logger.sys.__excepthook__')
    def test_rollbar_except_hook_reports_exception(self, mock_sys_hook, mock_report):
        """Test that rollbar_except_hook reports exception to rollbar."""
        from logger import rollbar_except_hook

        exc_type = Exception
        exc_value = Exception("Test error")
        traceback = None

        rollbar_except_hook(exc_type, exc_value, traceback)

        mock_report.assert_called_once_with((exc_type, exc_value, traceback))
        mock_sys_hook.assert_called_once_with(exc_type, exc_value, traceback)


class TestSetRollbarExceptionCatch:
    """Tests for set_rollbar_exception_catch function."""

    @patch('logger.sys')
    def test_set_rollbar_exception_catch_sets_hook(self, mock_sys):
        """Test that set_rollbar_exception_catch sets sys.excepthook."""
        from logger import set_rollbar_exception_catch, rollbar_except_hook

        set_rollbar_exception_catch()

        assert mock_sys.excepthook == rollbar_except_hook


class TestGetConsoleHandler:
    """Tests for get_console_handler function."""

    def test_get_console_handler_returns_stream_handler(self):
        """Test that get_console_handler returns a StreamHandler."""
        from logger import get_console_handler

        handler = get_console_handler()

        assert isinstance(handler, logging.StreamHandler)

    def test_get_console_handler_uses_stdout(self):
        """Test that get_console_handler uses stdout."""
        from logger import get_console_handler

        handler = get_console_handler()

        assert handler.stream == sys.stdout

    def test_get_console_handler_has_formatter(self):
        """Test that get_console_handler has a formatter."""
        from logger import get_console_handler

        handler = get_console_handler()

        assert handler.formatter is not None


class TestGetRollbarHandler:
    """Tests for get_rollbar_handler function."""

    @patch('logger.RollbarHandler')
    @patch('logger.config')
    def test_get_rollbar_handler_creates_handler(self, mock_config, mock_rollbar_handler_class):
        """Test that get_rollbar_handler creates RollbarHandler."""
        from logger import get_rollbar_handler

        mock_config.LOGLEVEL = 'WARNING'
        mock_config.ROLLBAR_ACCESS_TOKEN = 'test_token'
        mock_config.APP_ENV = 'production'

        mock_handler = MagicMock()
        mock_rollbar_handler_class.return_value = mock_handler

        result = get_rollbar_handler()

        assert result == mock_handler
        mock_rollbar_handler_class.assert_called_once_with(
            access_token='test_token',
            environment='production'
        )

    @patch('logger.RollbarHandler')
    @patch('logger.config')
    def test_get_rollbar_handler_sets_level(self, mock_config, mock_rollbar_handler_class):
        """Test that get_rollbar_handler sets log level."""
        from logger import get_rollbar_handler

        mock_config.LOGLEVEL = 'ERROR'
        mock_config.ROLLBAR_ACCESS_TOKEN = 'test_token'
        mock_config.APP_ENV = 'production'

        mock_handler = MagicMock()
        mock_rollbar_handler_class.return_value = mock_handler

        result = get_rollbar_handler()

        mock_handler.setLevel.assert_called_once_with(logging.ERROR)


class TestGetLogger:
    """Tests for get_logger function."""

    @patch('logger.config')
    def test_get_logger_returns_logger(self, mock_config):
        """Test that get_logger returns a logger instance."""
        from logger import get_logger

        mock_config.APP_ENV = 'development'
        mock_config.LOGLEVEL = 'INFO'
        mock_config.ROLLBAR_ACCESS_TOKEN = None

        logger = get_logger('test_logger')

        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'

    @patch('logger.config')
    def test_get_logger_clears_handlers(self, mock_config):
        """Test that get_logger clears existing handlers."""
        from logger import get_logger

        mock_config.APP_ENV = 'development'
        mock_config.LOGLEVEL = 'INFO'
        mock_config.ROLLBAR_ACCESS_TOKEN = None

        logger = get_logger('test_logger')

        # Logger should have exactly one handler (console)
        assert len(logger.handlers) == 1

    @patch('logger.config')
    def test_get_logger_sets_level(self, mock_config):
        """Test that get_logger sets log level."""
        from logger import get_logger

        mock_config.APP_ENV = 'development'
        mock_config.LOGLEVEL = 'INFO'
        mock_config.ROLLBAR_ACCESS_TOKEN = None

        logger = get_logger('test_logger')

        assert logger.level == logging.DEBUG  # Non-production uses DEBUG

    @patch('logger.config')
    def test_get_logger_adds_console_handler(self, mock_config):
        """Test that get_logger adds console handler."""
        from logger import get_logger

        mock_config.APP_ENV = 'development'
        mock_config.LOGLEVEL = 'INFO'
        mock_config.ROLLBAR_ACCESS_TOKEN = None

        logger = get_logger('test_logger')

        assert len(logger.handlers) >= 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    @patch('logger.config')
    def test_get_logger_disables_propagation(self, mock_config):
        """Test that get_logger disables propagation."""
        from logger import get_logger

        mock_config.APP_ENV = 'development'
        mock_config.LOGLEVEL = 'INFO'
        mock_config.ROLLBAR_ACCESS_TOKEN = None

        logger = get_logger('test_logger')

        assert logger.propagate is False


class TestSetRequestExceptionSignal:
    """Tests for set_request_exception_signal function."""

    @patch('logger.rollbar.contrib.flask.report_exception')
    @patch('logger.got_request_exception.connect')
    def test_set_request_exception_signal_connects(self, mock_connect, mock_report):
        """Test that set_request_exception_signal connects signal."""
        from logger import set_request_exception_signal

        mock_app = MagicMock()

        set_request_exception_signal(mock_app)

        mock_connect.assert_called_once_with(mock_report, mock_app)
