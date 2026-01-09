"""
Unit tests for flask/app/__init__.py
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from flask import Flask
from rococo.models.versioned_model import ModelValidationError
from common.helpers.exceptions import InputValidationError, APIException


class TestCreateApp:
    """Tests for create_app function."""

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_returns_flask_instance(self, mock_get_config, mock_cors,
                                               mock_pooled_conn, mock_init_views,
                                               mock_set_signal):
        """Test that create_app returns a Flask application instance."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        assert isinstance(app, Flask)
        assert app is not None

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_initializes_cors(self, mock_get_config, mock_cors,
                                         mock_pooled_conn, mock_init_views,
                                         mock_set_signal):
        """Test that create_app initializes CORS."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        mock_cors.assert_called_once()

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_initializes_pooled_connection(self, mock_get_config, mock_cors,
                                                      mock_pooled_conn, mock_init_views,
                                                      mock_set_signal):
        """Test that create_app initializes PooledConnectionPlugin."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        mock_pooled_conn.assert_called_once()
        call_args = mock_pooled_conn.call_args
        assert call_args[1]['database_type'] == "postgres"

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_registers_views(self, mock_get_config, mock_cors,
                                        mock_pooled_conn, mock_init_views,
                                        mock_set_signal):
        """Test that create_app registers views."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        mock_init_views.assert_called_once()

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_root_route(self, mock_get_config, mock_cors,
                                   mock_pooled_conn, mock_init_views,
                                   mock_set_signal):
        """Test that root route is registered."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert b'Welcome to Rococo Sample API' in response.data

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_model_validation_error_handler(self, mock_get_config, mock_cors,
                                                       mock_pooled_conn, mock_init_views,
                                                       mock_set_signal):
        """Test that ModelValidationError handler is registered."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        # Verify error handler exists
        assert ModelValidationError in app.error_handler_spec[None]

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_input_validation_error_handler(self, mock_get_config, mock_cors,
                                                       mock_pooled_conn, mock_init_views,
                                                       mock_set_signal):
        """Test that InputValidationError handler is registered."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        # Verify error handler exists
        assert InputValidationError in app.error_handler_spec[None]

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_api_exception_handler(self, mock_get_config, mock_cors,
                                              mock_pooled_conn, mock_init_views,
                                              mock_set_signal):
        """Test that APIException handler is registered."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        app = create_app()

        # Verify error handler exists
        assert APIException in app.error_handler_spec[None]

    @patch('flask.app.__init__.set_request_exception_signal')
    @patch('flask.app.__init__.initialize_views')
    @patch('flask.app.__init__.PooledConnectionPlugin')
    @patch('flask.app.__init__.CORS')
    @patch('flask.app.__init__.get_config')
    def test_create_app_sets_config(self, mock_get_config, mock_cors,
                                    mock_pooled_conn, mock_init_views,
                                    mock_set_signal):
        """Test that create_app sets config from get_config."""
        from flask.app import create_app

        mock_config = MagicMock()
        mock_config.TEST_VALUE = 'test'
        mock_get_config.return_value = mock_config

        app = create_app()

        mock_get_config.assert_called_once()
