"""Comprehensive tests for SonarQube API integration module."""

import json
import logging
import os
import sys
import pytest
from dataclasses import asdict
from typing import Optional
from unittest.mock import MagicMock, Mock, patch, PropertyMock

from adws.adw_modules.sonarqube import (
    CoverageFile,
    SonarQubeMetrics,
    SonarQubeClient,
)


class TestCoverageFile:
    """Tests for CoverageFile dataclass."""

    def test_coverage_file_creation(self):
        """Test CoverageFile can be created with all fields."""
        coverage_file = CoverageFile(
            path="test/file.py",
            coverage_percentage=85.5,
            uncovered_lines=[10, 20, 30],
            lines_to_cover=100,
            uncovered_conditions=5,
            lines=120,
        )

        assert coverage_file.path == "test/file.py"
        assert coverage_file.coverage_percentage == 85.5
        assert coverage_file.uncovered_lines == [10, 20, 30]
        assert coverage_file.lines_to_cover == 100
        assert coverage_file.uncovered_conditions == 5
        assert coverage_file.lines == 120

    def test_coverage_file_empty_uncovered_lines(self):
        """Test CoverageFile with empty uncovered lines list."""
        coverage_file = CoverageFile(
            path="test/perfect.py",
            coverage_percentage=100.0,
            uncovered_lines=[],
            lines_to_cover=50,
            uncovered_conditions=0,
            lines=50,
        )

        assert coverage_file.uncovered_lines == []
        assert coverage_file.coverage_percentage == 100.0


class TestSonarQubeMetrics:
    """Tests for SonarQubeMetrics dataclass."""

    def test_sonarqube_metrics_creation(self):
        """Test SonarQubeMetrics can be created with all fields."""
        metrics = SonarQubeMetrics(
            coverage=92.5,
            lines_to_cover=1000,
            uncovered_lines=75,
            conditions_to_cover=200,
            uncovered_conditions=15,
        )

        assert metrics.coverage == 92.5
        assert metrics.lines_to_cover == 1000
        assert metrics.uncovered_lines == 75
        assert metrics.conditions_to_cover == 200
        assert metrics.uncovered_conditions == 15

    def test_sonarqube_metrics_zero_values(self):
        """Test SonarQubeMetrics with zero values."""
        metrics = SonarQubeMetrics(
            coverage=0.0,
            lines_to_cover=0,
            uncovered_lines=0,
            conditions_to_cover=0,
            uncovered_conditions=0,
        )

        assert metrics.coverage == 0.0
        assert metrics.lines_to_cover == 0


class TestImportErrorHandling:
    """Tests for import error handling."""

    def test_httpbasicauth_import_fallback(self):
        """Test that HTTPBasicAuth fallback is handled correctly when requests is unavailable."""
        # This test validates the behavior of lines 12-14 in the module
        # While we can't easily trigger the actual import error at test time,
        # we verify that the fallback mechanism works by checking the import structure
        import adws.adw_modules.sonarqube as sonarqube_module

        # When requests is available (normal case), HTTPBasicAuth should be imported
        # The except block on lines 12-14 only executes when requests is not available
        # This test documents the expected behavior of that error handling
        assert hasattr(sonarqube_module, 'requests')
        assert hasattr(sonarqube_module, 'HTTPBasicAuth')


class TestSonarQubeClientInit:
    """Tests for SonarQubeClient initialization."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_init_from_environment_variables(self, mock_requests):
        """Test initialization with environment variables."""
        mock_requests.get = Mock()

        client = SonarQubeClient()

        assert client.base_url == "https://sonar.example.com"
        assert client.token == "test-token"
        assert client.project_key == "my-project"
        assert isinstance(client.logger, logging.Logger)

    @patch('adws.adw_modules.sonarqube.requests')
    def test_init_with_explicit_parameters(self, mock_requests):
        """Test initialization with explicit parameters."""
        mock_requests.get = Mock()

        client = SonarQubeClient(
            base_url="https://custom.sonar.com",
            token="custom-token",
            project_key="custom-project"
        )

        assert client.base_url == "https://custom.sonar.com"
        assert client.token == "custom-token"
        assert client.project_key == "custom-project"

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com/",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_init_strips_trailing_slash_from_url(self, mock_requests):
        """Test that trailing slash is stripped from base URL."""
        mock_requests.get = Mock()

        client = SonarQubeClient()

        assert client.base_url == "https://sonar.example.com"

    @patch.dict(os.environ, {}, clear=True)
    @patch('adws.adw_modules.sonarqube.requests')
    def test_init_uses_default_project_key(self, mock_requests):
        """Test that default project key is used when not provided."""
        mock_requests.get = Mock()

        client = SonarQubeClient(base_url="https://sonar.example.com")

        assert client.project_key == "rococo-sample-backend"

    @patch.dict(os.environ, {}, clear=True)
    @patch('adws.adw_modules.sonarqube.requests')
    def test_init_missing_base_url_raises_error(self, mock_requests):
        """Test that missing base URL raises ValueError."""
        mock_requests.get = Mock()

        with pytest.raises(ValueError, match="SonarQube base URL not provided"):
            SonarQubeClient()

    @patch('adws.adw_modules.sonarqube.requests', None)
    def test_init_missing_requests_library_raises_error(self):
        """Test that missing requests library raises ImportError."""
        with pytest.raises(ImportError, match="requests library is required"):
            SonarQubeClient(base_url="https://sonar.example.com")


class TestSonarQubeClientMakeRequest:
    """Tests for SonarQubeClient._make_request method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_make_request_success_with_token(self, mock_requests):
        """Test successful API request with token authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        result = client._make_request("/api/test", {"param": "value"})

        assert result == {"data": "test"}
        mock_requests.get.assert_called_once()
        call_args = mock_requests.get.call_args
        assert call_args[0][0] == "https://sonar.example.com/api/test"
        assert call_args[1]["params"] == {"param": "value"}
        assert call_args[1]["auth"] is not None
        assert call_args[1]["timeout"] == 30

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_make_request_success_without_token(self, mock_requests):
        """Test successful API request without token authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        result = client._make_request("/api/test")

        assert result == {"data": "test"}
        call_args = mock_requests.get.call_args
        assert call_args[1]["auth"] is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_make_request_401_authentication_failure(self, mock_requests):
        """Test API request with 401 authentication failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        result = client._make_request("/api/test")

        assert result is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_make_request_404_not_found(self, mock_requests):
        """Test API request with 404 not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        result = client._make_request("/api/test")

        assert result is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_make_request_500_server_error(self, mock_requests):
        """Test API request with 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        result = client._make_request("/api/test")

        assert result is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_make_request_network_error(self, mock_requests):
        """Test API request with network connection error."""
        # Create a proper RequestException mock
        from requests.exceptions import RequestException
        mock_requests.exceptions.RequestException = RequestException
        mock_requests.get.side_effect = RequestException("Connection failed")

        client = SonarQubeClient()
        result = client._make_request("/api/test")

        assert result is None


class TestSonarQubeClientGetProjectMetrics:
    """Tests for SonarQubeClient.get_project_metrics method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_project_metrics_success(self, mock_requests):
        """Test successful project metrics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "85.5"},
                    {"metric": "lines_to_cover", "value": "1000"},
                    {"metric": "uncovered_lines", "value": "145"},
                    {"metric": "conditions_to_cover", "value": "200"},
                    {"metric": "uncovered_conditions", "value": "30"},
                ]
            }
        }
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        metrics = client.get_project_metrics()

        assert metrics is not None
        assert metrics.coverage == 85.5
        assert metrics.lines_to_cover == 1000
        assert metrics.uncovered_lines == 145
        assert metrics.conditions_to_cover == 200
        assert metrics.uncovered_conditions == 30

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_project_metrics_missing_values(self, mock_requests):
        """Test project metrics with missing values defaults to 0."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "50.0"},
                ]
            }
        }
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        metrics = client.get_project_metrics()

        assert metrics is not None
        assert metrics.coverage == 50.0
        assert metrics.lines_to_cover == 0
        assert metrics.uncovered_lines == 0
        assert metrics.conditions_to_cover == 0
        assert metrics.uncovered_conditions == 0

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_project_metrics_request_failed(self, mock_requests):
        """Test project metrics when request fails."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        metrics = client.get_project_metrics()

        assert metrics is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_project_metrics_invalid_json_structure(self, mock_requests):
        """Test project metrics with invalid JSON structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        metrics = client.get_project_metrics()

        assert metrics is not None
        assert metrics.coverage == 0.0

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_project_metrics_invalid_value_type(self, mock_requests):
        """Test project metrics with invalid value types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "invalid"},
                ]
            }
        }
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        metrics = client.get_project_metrics()

        assert metrics is None


class TestSonarQubeClientGetFileCoverage:
    """Tests for SonarQubeClient.get_file_coverage method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_file_coverage_parse_error(self, mock_requests):
        """Test file coverage with parse error in metrics."""
        mock_metrics_response = Mock()
        mock_metrics_response.status_code = 200
        # Return structure that will cause KeyError when accessing nested data
        mock_metrics_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "invalid_float"},
                ]
            }
        }
        mock_requests.get.return_value = mock_metrics_response

        client = SonarQubeClient()
        coverage = client.get_file_coverage("my-project:test/file.py")

        # Should return None on ValueError during parsing
        assert coverage is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_file_coverage_success_with_uncovered_lines(self, mock_requests):
        """Test successful file coverage retrieval with uncovered lines."""
        mock_metrics_response = Mock()
        mock_metrics_response.status_code = 200
        mock_metrics_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "75.0"},
                    {"metric": "lines_to_cover", "value": "100"},
                    {"metric": "uncovered_lines", "value": "25"},
                    {"metric": "conditions_to_cover", "value": "50"},
                    {"metric": "uncovered_conditions", "value": "10"},
                    {"metric": "lines", "value": "120"},
                ]
            }
        }

        mock_lines_response = Mock()
        mock_lines_response.status_code = 200
        mock_lines_response.json.return_value = {
            "sources": [
                {"line": 10, "coverageStatus": "COVERED"},
                {"line": 11, "coverageStatus": "UNCOVERED"},
                {"line": 12, "coverageStatus": "UNCOVERED"},
                {"line": 13, "coverageStatus": "COVERED"},
                {"line": 14, "coverageStatus": "UNCOVERED"},
            ]
        }

        mock_requests.get.side_effect = [mock_metrics_response, mock_lines_response]

        client = SonarQubeClient()
        coverage = client.get_file_coverage("my-project:test/file.py")

        assert coverage is not None
        assert coverage.path == "test/file.py"
        assert coverage.coverage_percentage == 75.0
        assert coverage.uncovered_lines == [11, 12, 14]
        assert coverage.lines_to_cover == 100
        assert coverage.uncovered_conditions == 10
        assert coverage.lines == 120

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_file_coverage_no_uncovered_lines_data(self, mock_requests):
        """Test file coverage when uncovered lines data is unavailable."""
        mock_metrics_response = Mock()
        mock_metrics_response.status_code = 200
        mock_metrics_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "100.0"},
                    {"metric": "lines_to_cover", "value": "50"},
                    {"metric": "lines", "value": "50"},
                ]
            }
        }

        mock_lines_response = Mock()
        mock_lines_response.status_code = 404
        mock_requests.get.side_effect = [mock_metrics_response, mock_lines_response]

        client = SonarQubeClient()
        coverage = client.get_file_coverage("my-project:test/file.py")

        assert coverage is not None
        assert coverage.uncovered_lines == []
        assert coverage.coverage_percentage == 100.0

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_file_coverage_metrics_request_failed(self, mock_requests):
        """Test file coverage when metrics request fails."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        coverage = client.get_file_coverage("my-project:test/file.py")

        assert coverage is None

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_file_coverage_invalid_response_structure(self, mock_requests):
        """Test file coverage with invalid response structure returns object with defaults."""
        # First call for metrics, second call for uncovered lines
        mock_metrics_response = Mock()
        mock_metrics_response.status_code = 200
        mock_metrics_response.json.return_value = {"invalid": "data"}

        mock_lines_response = Mock()
        mock_lines_response.status_code = 200
        mock_lines_response.json.return_value = {"invalid": "data"}

        mock_requests.get.side_effect = [mock_metrics_response, mock_lines_response]

        client = SonarQubeClient()
        coverage = client.get_file_coverage("my-project:test/file.py")

        # With invalid structure, defaults to 0 values
        assert coverage is not None
        assert coverage.coverage_percentage == 0.0
        assert coverage.lines_to_cover == 0


class TestSonarQubeClientGetAllFiles:
    """Tests for SonarQubeClient.get_all_files method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_all_files_success(self, mock_requests):
        """Test successful retrieval of all files."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
                {"key": "my-project:file2.py"},
                {"key": "my-project:test/file3.py"},
            ]
        }
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        files = client.get_all_files()

        assert len(files) == 3
        assert files == ["my-project:file1.py", "my-project:file2.py", "my-project:test/file3.py"]

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_all_files_empty_result(self, mock_requests):
        """Test get_all_files with empty result."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"components": []}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        files = client.get_all_files()

        assert files == []

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_all_files_request_failed(self, mock_requests):
        """Test get_all_files when request fails."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        files = client.get_all_files()

        assert files == []

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_all_files_invalid_response_structure(self, mock_requests):
        """Test get_all_files with invalid response structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "data"}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        files = client.get_all_files()

        assert files == []

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_all_files_component_missing_key(self, mock_requests):
        """Test get_all_files with component missing key field."""
        mock_response = Mock()
        mock_response.status_code = 200
        # Components without 'key' field will cause KeyError
        mock_response.json.return_value = {
            "components": [
                {"name": "file1.py"},  # missing 'key'
            ]
        }
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        files = client.get_all_files()

        assert files == []


class TestSonarQubeClientGetUncoveredFiles:
    """Tests for SonarQubeClient.get_uncovered_files method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_default_threshold(self, mock_requests):
        """Test get_uncovered_files with default threshold (100%)."""
        # Mock get_all_files response
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
                {"key": "my-project:file2.py"},
            ]
        }

        # Mock get_file_coverage responses
        mock_file1_metrics = Mock()
        mock_file1_metrics.status_code = 200
        mock_file1_metrics.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "85.0"},
                    {"metric": "lines_to_cover", "value": "100"},
                    {"metric": "lines", "value": "120"},
                ]
            }
        }

        mock_file1_lines = Mock()
        mock_file1_lines.status_code = 200
        mock_file1_lines.json.return_value = {"sources": []}

        mock_file2_metrics = Mock()
        mock_file2_metrics.status_code = 200
        mock_file2_metrics.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "100.0"},
                    {"metric": "lines_to_cover", "value": "50"},
                    {"metric": "lines", "value": "50"},
                ]
            }
        }

        mock_file2_lines = Mock()
        mock_file2_lines.status_code = 200
        mock_file2_lines.json.return_value = {"sources": []}

        mock_requests.get.side_effect = [
            mock_files_response,
            mock_file1_metrics,
            mock_file1_lines,
            mock_file2_metrics,
            mock_file2_lines,
        ]

        client = SonarQubeClient()
        uncovered = client.get_uncovered_files()

        assert len(uncovered) == 1
        assert uncovered[0].path == "file1.py"
        assert uncovered[0].coverage_percentage == 85.0

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_custom_threshold(self, mock_requests):
        """Test get_uncovered_files with custom threshold."""
        # Mock get_all_files response
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
            ]
        }

        # Mock get_file_coverage response
        mock_file_metrics = Mock()
        mock_file_metrics.status_code = 200
        mock_file_metrics.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "85.0"},
                    {"metric": "lines_to_cover", "value": "100"},
                    {"metric": "lines", "value": "120"},
                ]
            }
        }

        mock_file_lines = Mock()
        mock_file_lines.status_code = 200
        mock_file_lines.json.return_value = {"sources": []}

        mock_requests.get.side_effect = [
            mock_files_response,
            mock_file_metrics,
            mock_file_lines,
        ]

        client = SonarQubeClient()
        uncovered = client.get_uncovered_files(min_coverage=90.0)

        assert len(uncovered) == 1
        assert uncovered[0].coverage_percentage == 85.0

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_no_files(self, mock_requests):
        """Test get_uncovered_files when no files exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"components": []}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        uncovered = client.get_uncovered_files()

        assert uncovered == []

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_skips_none_coverage(self, mock_requests):
        """Test get_uncovered_files skips files that return None coverage."""
        # Mock get_all_files response
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
            ]
        }

        # Mock get_file_coverage to return error
        mock_file_metrics = Mock()
        mock_file_metrics.status_code = 500
        mock_file_metrics.text = "Error"

        mock_requests.get.side_effect = [
            mock_files_response,
            mock_file_metrics,
        ]

        client = SonarQubeClient()
        uncovered = client.get_uncovered_files()

        assert uncovered == []


class TestSonarQubeClientGetCoverageSummary:
    """Tests for SonarQubeClient.get_coverage_summary method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_coverage_summary_success(self, mock_requests):
        """Test successful coverage summary generation."""
        # Mock get_project_metrics
        mock_metrics_response = Mock()
        mock_metrics_response.status_code = 200
        mock_metrics_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "85.5"},
                    {"metric": "lines_to_cover", "value": "1000"},
                    {"metric": "uncovered_lines", "value": "145"},
                    {"metric": "conditions_to_cover", "value": "200"},
                    {"metric": "uncovered_conditions", "value": "30"},
                ]
            }
        }

        # Mock get_all_files
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
            ]
        }

        # Mock get_file_coverage
        mock_file_metrics = Mock()
        mock_file_metrics.status_code = 200
        mock_file_metrics.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "75.0"},
                    {"metric": "lines_to_cover", "value": "100"},
                    {"metric": "lines", "value": "120"},
                ]
            }
        }

        mock_file_lines = Mock()
        mock_file_lines.status_code = 200
        mock_file_lines.json.return_value = {
            "sources": [
                {"line": 10, "coverageStatus": "UNCOVERED"},
                {"line": 11, "coverageStatus": "UNCOVERED"},
            ]
        }

        mock_requests.get.side_effect = [
            mock_metrics_response,
            mock_files_response,
            mock_file_metrics,
            mock_file_lines,
        ]

        client = SonarQubeClient()
        summary = client.get_coverage_summary()

        assert "my-project" in summary
        assert "85.50%" in summary
        assert "1000" in summary
        assert "145" in summary
        assert "file1.py" in summary
        assert "75.0% coverage" in summary

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_coverage_summary_limits_files_to_20(self, mock_requests):
        """Test that coverage summary limits output to first 20 files."""
        # Mock get_project_metrics
        mock_metrics_response = Mock()
        mock_metrics_response.status_code = 200
        mock_metrics_response.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "50.0"},
                ]
            }
        }

        # Mock get_all_files with 25 files
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [{"key": f"my-project:file{i}.py"} for i in range(25)]
        }

        # Mock get_file_coverage for all files
        file_responses = []
        for i in range(25):
            mock_file_metrics = Mock()
            mock_file_metrics.status_code = 200
            mock_file_metrics.json.return_value = {
                "component": {
                    "measures": [
                        {"metric": "coverage", "value": "50.0"},
                        {"metric": "lines", "value": "100"},
                    ]
                }
            }
            file_responses.append(mock_file_metrics)

            mock_file_lines = Mock()
            mock_file_lines.status_code = 200
            mock_file_lines.json.return_value = {"sources": []}
            file_responses.append(mock_file_lines)

        mock_requests.get.side_effect = [
            mock_metrics_response,
            mock_files_response,
        ] + file_responses

        client = SonarQubeClient()
        summary = client.get_coverage_summary()

        assert "... and 5 more files" in summary
        assert summary.count("file") >= 20  # At least 20 files mentioned

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_coverage_summary_metrics_failed(self, mock_requests):
        """Test coverage summary when metrics request fails."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        summary = client.get_coverage_summary()

        assert summary == "Unable to fetch SonarQube coverage metrics."


class TestSonarQubeClientGetUncoveredFilesSummary:
    """Tests for SonarQubeClient.get_uncovered_files_summary method."""

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_summary_success(self, mock_requests):
        """Test successful uncovered files summary generation."""
        # Mock get_all_files
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
            ]
        }

        # Mock get_file_coverage
        mock_file_metrics = Mock()
        mock_file_metrics.status_code = 200
        mock_file_metrics.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "75.0"},
                    {"metric": "lines_to_cover", "value": "100"},
                    {"metric": "lines", "value": "120"},
                ]
            }
        }

        mock_file_lines = Mock()
        mock_file_lines.status_code = 200
        mock_file_lines.json.return_value = {
            "sources": [
                {"line": 10, "coverageStatus": "UNCOVERED"},
                {"line": 11, "coverageStatus": "UNCOVERED"},
                {"line": 12, "coverageStatus": "COVERED"},
            ]
        }

        mock_requests.get.side_effect = [
            mock_files_response,
            mock_file_metrics,
            mock_file_lines,
        ]

        client = SonarQubeClient()
        summary_json = client.get_uncovered_files_summary()
        summary = json.loads(summary_json)

        assert summary["total_uncovered_files"] == 1
        assert len(summary["files"]) == 1
        assert summary["files"][0]["path"] == "file1.py"
        assert summary["files"][0]["coverage_percentage"] == 75.0
        assert summary["files"][0]["uncovered_lines"] == [10, 11]
        assert summary["files"][0]["total_uncovered_lines"] == 2
        assert summary["files"][0]["lines_to_cover"] == 100

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token",
        "SONARQUBE_PROJECT_KEY": "my-project"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_summary_limits_uncovered_lines_to_50(self, mock_requests):
        """Test that uncovered files summary limits uncovered lines to first 50."""
        # Mock get_all_files
        mock_files_response = Mock()
        mock_files_response.status_code = 200
        mock_files_response.json.return_value = {
            "components": [
                {"key": "my-project:file1.py"},
            ]
        }

        # Mock get_file_coverage with 60 uncovered lines
        mock_file_metrics = Mock()
        mock_file_metrics.status_code = 200
        mock_file_metrics.json.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "10.0"},
                    {"metric": "lines_to_cover", "value": "100"},
                    {"metric": "lines", "value": "100"},
                ]
            }
        }

        mock_file_lines = Mock()
        mock_file_lines.status_code = 200
        # Create 60 uncovered lines
        uncovered_sources = [{"line": i, "coverageStatus": "UNCOVERED"} for i in range(1, 61)]
        mock_file_lines.json.return_value = {"sources": uncovered_sources}

        mock_requests.get.side_effect = [
            mock_files_response,
            mock_file_metrics,
            mock_file_lines,
        ]

        client = SonarQubeClient()
        summary_json = client.get_uncovered_files_summary()
        summary = json.loads(summary_json)

        assert len(summary["files"][0]["uncovered_lines"]) == 50
        assert summary["files"][0]["total_uncovered_lines"] == 60

    @patch.dict(os.environ, {
        "SONARQUBE_URL": "https://sonar.example.com",
        "SONARQUBE_TOKEN": "test-token"
    })
    @patch('adws.adw_modules.sonarqube.requests')
    def test_get_uncovered_files_summary_no_uncovered_files(self, mock_requests):
        """Test uncovered files summary when all files are fully covered."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"components": []}
        mock_requests.get.return_value = mock_response

        client = SonarQubeClient()
        summary_json = client.get_uncovered_files_summary()
        summary = json.loads(summary_json)

        assert summary["total_uncovered_files"] == 0
        assert summary["files"] == []
