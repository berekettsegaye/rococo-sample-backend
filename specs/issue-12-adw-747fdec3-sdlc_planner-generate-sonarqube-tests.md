# Chore: Generate tests for uncovered code

## Metadata
issue_number: `12`
adw_id: `747fdec3`
issue_json: `{"number": 12, "title": "Generate tests for uncovered code", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Generate comprehensive test coverage for the SonarQube integration module (`adws/adw_modules/sonarqube.py`) to reach 100% code coverage. This module provides SonarQube API integration for fetching code coverage data, including project metrics, file-level coverage, and uncovered lines detection.

The module contains:
- `CoverageFile` dataclass for file-level coverage data
- `SonarQubeMetrics` dataclass for project-level metrics
- `SonarQubeClient` class with methods for API interaction, authentication, and coverage reporting

## Relevant Files
Use these files to resolve the chore:

- **adws/adw_modules/sonarqube.py** (305 lines)
  - Primary file requiring test coverage
  - Contains SonarQube API client implementation
  - Includes data classes for coverage metrics and file coverage
  - Methods to test: `__init__`, `_make_request`, `get_project_metrics`, `get_file_coverage`, `get_all_files`, `get_uncovered_files`, `get_coverage_summary`, `get_uncovered_files_summary`

- **tests/conftest.py**
  - Provides shared pytest fixtures
  - Contains test environment setup and mock objects
  - Will be referenced for fixture patterns

- **pyproject.toml**
  - Contains pytest configuration
  - Defines coverage settings and test paths
  - Specifies test source paths including adws/adw_modules

### New Files

- **tests/adw_modules/__init__.py**
  - Required to make adw_modules test directory a Python package

- **tests/adw_modules/test_sonarqube.py**
  - Comprehensive test suite for sonarqube.py module
  - Tests for all classes, methods, and edge cases
  - Includes mocking of external dependencies (requests, environment variables)

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create test directory structure
- Create `tests/adw_modules/` directory if it doesn't exist
- Create `tests/adw_modules/__init__.py` to make it a proper Python package

### 2. Analyze sonarqube.py module for test requirements
- Identify all classes: `CoverageFile`, `SonarQubeMetrics`, `SonarQubeClient`
- Identify all methods in `SonarQubeClient`: `__init__`, `_make_request`, `get_project_metrics`, `get_file_coverage`, `get_all_files`, `get_uncovered_files`, `get_coverage_summary`, `get_uncovered_files_summary`
- Identify all code paths including success cases, error cases, and edge cases
- Identify external dependencies to mock: `requests` library, environment variables, HTTP responses

### 3. Create comprehensive test suite
- Create `tests/adw_modules/test_sonarqube.py` with the following test coverage:

  **Test fixtures:**
  - Mock SonarQube responses (success, 401, 404, 500 errors)
  - Mock environment variables
  - Mock requests library responses

  **Test CoverageFile dataclass:**
  - Test instantiation with valid data
  - Test all fields are properly typed

  **Test SonarQubeMetrics dataclass:**
  - Test instantiation with valid data
  - Test all fields are properly typed

  **Test SonarQubeClient.__init__:**
  - Test initialization with explicit parameters
  - Test initialization with environment variables
  - Test initialization without base_url (should raise ValueError)
  - Test initialization without requests library (should raise ImportError)
  - Test URL stripping of trailing slashes

  **Test SonarQubeClient._make_request:**
  - Test successful request (200 response)
  - Test authentication with token
  - Test 401 unauthorized response
  - Test 404 not found response
  - Test other error status codes (500, 503)
  - Test request exceptions (timeout, connection error)
  - Test request with query parameters

  **Test SonarQubeClient.get_project_metrics:**
  - Test successful metrics retrieval
  - Test with missing metrics in response
  - Test with malformed response data
  - Test when API request fails
  - Test parsing of all metric fields

  **Test SonarQubeClient.get_file_coverage:**
  - Test successful file coverage retrieval
  - Test with uncovered lines data
  - Test with missing coverage data
  - Test when sources/lines API fails
  - Test file key path extraction
  - Test malformed response handling

  **Test SonarQubeClient.get_all_files:**
  - Test successful file list retrieval
  - Test with empty project
  - Test when API request fails
  - Test malformed response handling

  **Test SonarQubeClient.get_uncovered_files:**
  - Test with default min_coverage (100%)
  - Test with custom min_coverage threshold
  - Test with all files fully covered
  - Test with mix of covered and uncovered files
  - Test with no files in project

  **Test SonarQubeClient.get_coverage_summary:**
  - Test successful summary generation
  - Test with uncovered files
  - Test with more than 20 uncovered files (pagination)
  - Test when metrics fetch fails
  - Test formatting of output string

  **Test SonarQubeClient.get_uncovered_files_summary:**
  - Test JSON output format
  - Test with multiple uncovered files
  - Test with files having many uncovered lines (50+ lines truncation)
  - Test with zero uncovered files
  - Test JSON structure and fields

### 4. Update pyproject.toml coverage configuration
- Add `adws/adw_modules/*` to the coverage include paths in `[tool.coverage.run]` section
- Ensure pytest can discover and run tests in the new test directory

### 5. Run tests to verify coverage
- Execute `pytest tests/adw_modules/test_sonarqube.py -v` to run new tests
- Execute `pytest tests/adw_modules/test_sonarqube.py --cov=adws/adw_modules/sonarqube --cov-report=term-missing` to verify 100% coverage
- Fix any test failures or coverage gaps identified

### 6. Run full test suite validation
- Execute all validation commands to ensure no regressions
- Verify that all tests pass
- Verify that coverage for sonarqube.py reaches 100%

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/adw_modules/test_sonarqube.py -v` - Run new sonarqube tests to validate functionality
- `pytest tests/adw_modules/test_sonarqube.py --cov=adws/adw_modules/sonarqube --cov-report=term-missing -v` - Verify 100% coverage for sonarqube.py module
- `pytest tests/ -v` - Run all tests to validate zero regressions across entire test suite

## Notes
- The sonarqube.py module uses the `requests` library which must be mocked in tests to avoid actual HTTP calls
- Environment variables (SONARQUBE_URL, SONARQUBE_TOKEN, SONARQUBE_PROJECT_KEY) must be mocked in tests
- The module has error handling for missing requests library, authentication failures, and various HTTP error codes - all must be tested
- The module includes logging - consider using pytest caplog fixture to verify log messages
- Mock data should match the actual SonarQube API response format to ensure tests are realistic
- The file is located in `adws/adw_modules/` which is not currently in the pyproject.toml coverage include list - this needs to be added
- Consider using `@pytest.mark.parametrize` for testing multiple similar scenarios (e.g., different HTTP status codes)
- All external dependencies should be mocked using `unittest.mock` or `pytest-mock`
