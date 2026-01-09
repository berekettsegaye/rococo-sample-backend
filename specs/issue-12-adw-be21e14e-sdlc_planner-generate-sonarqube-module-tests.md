# Chore: Generate tests for uncovered code

## Metadata
issue_number: `12`
adw_id: `be21e14e`
issue_json: `{"number": 12, "title": "Generate tests for uncovered code", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Generate comprehensive test cases for the `adw_modules/sonarqube.py` module to achieve 100% code coverage. The SonarQube module provides API integration for fetching code coverage data and is currently untested. This chore will create a complete test suite that validates all functionality including:
- SonarQube client initialization
- API request handling and authentication
- Project metrics retrieval
- File coverage analysis
- Error handling for various HTTP status codes
- Coverage summary generation

## Relevant Files
Use these files to resolve the chore:

- `adws/adw_modules/sonarqube.py` - The main source file that needs test coverage. Contains the SonarQubeClient class with methods for fetching coverage data, metrics, and generating summaries.
- `tests/conftest.py` - Contains shared pytest fixtures and test configuration. We'll use fixtures like `mock_config` and potentially create new mocks for the requests library.
- `pyproject.toml` - Contains pytest configuration and coverage settings. Defines test paths, coverage sources, and which files should be included in coverage reports.
- `.claude/commands/test.md` - Documentation for test generation guidelines. Provides test structure patterns and best practices for the project.

### New Files
- `tests/test_sonarqube.py` - New test file containing comprehensive test cases for the SonarQube module, following the existing test patterns in the codebase.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Analyze the SonarQube module structure
- Read and understand all classes, methods, and functionality in `adws/adw_modules/sonarqube.py`
- Identify all code paths that need testing including:
  - `SonarQubeClient.__init__()` initialization with different parameter combinations
  - `_make_request()` method with various HTTP response codes (200, 401, 404, others)
  - `get_project_metrics()` method for successful and failed requests
  - `get_file_coverage()` method with different file keys
  - `get_all_files()` method for file listing
  - `get_uncovered_files()` method with different coverage thresholds
  - `get_coverage_summary()` method for formatting output
  - `get_uncovered_files_summary()` method for JSON formatting
- Note all error handling branches and edge cases
- Identify dependencies (requests library, HTTPBasicAuth, environment variables)

### Step 2: Design comprehensive test cases
- Create test cases for successful operations (happy path)
- Create test cases for error conditions:
  - Missing environment variables
  - Failed API authentication (401 errors)
  - Missing project/endpoint (404 errors)
  - Network errors and timeouts
  - Invalid response data formats
  - Missing requests library
- Create test cases for edge cases:
  - Empty responses
  - Large file lists
  - Files with 0% or 100% coverage
  - Different min_coverage thresholds
- Plan use of mocks for:
  - `requests.get()` calls
  - `HTTPBasicAuth` authentication
  - Environment variables
  - Logger calls

### Step 3: Create the test file with fixtures
- Create `tests/test_sonarqube.py`
- Import necessary testing libraries (pytest, unittest.mock, dataclasses)
- Create pytest fixtures for:
  - Mock SonarQube responses for different API endpoints
  - Mock environment variables
  - Mock requests library responses
  - Sample coverage data structures
- Organize fixtures to be reusable across multiple test methods

### Step 4: Implement test cases for initialization and authentication
- Test `SonarQubeClient.__init__()`:
  - Test with all parameters provided
  - Test with environment variables only
  - Test with missing requests library
  - Test with missing base_url
  - Test with default project_key
- Test authentication setup in `_make_request()`:
  - Test requests with token authentication
  - Test requests without token
  - Test HTTPBasicAuth configuration

### Step 5: Implement test cases for API request handling
- Test `_make_request()` method:
  - Test successful 200 response with valid JSON
  - Test 401 unauthorized response
  - Test 404 not found response
  - Test other error status codes
  - Test network timeout exceptions
  - Test connection errors
  - Test invalid JSON responses

### Step 6: Implement test cases for metrics and coverage methods
- Test `get_project_metrics()`:
  - Test successful metrics retrieval
  - Test with missing measures data
  - Test with invalid metric values
  - Test API request failure
- Test `get_file_coverage()`:
  - Test successful file coverage retrieval
  - Test with uncovered lines data
  - Test with missing coverage data
  - Test file key path extraction
- Test `get_all_files()`:
  - Test successful file list retrieval
  - Test with empty components list
  - Test API failure
- Test `get_uncovered_files()`:
  - Test with default 100% threshold
  - Test with custom threshold (e.g., 80%)
  - Test with no uncovered files
  - Test with multiple uncovered files

### Step 7: Implement test cases for summary methods
- Test `get_coverage_summary()`:
  - Test with successful metrics and uncovered files
  - Test with failed metrics retrieval
  - Test with many uncovered files (>20 truncation)
  - Test output format and string content
- Test `get_uncovered_files_summary()`:
  - Test JSON output structure
  - Test with multiple uncovered files
  - Test uncovered lines truncation (>50 lines)
  - Test total_uncovered_files count

### Step 8: Implement test cases for data classes
- Test `CoverageFile` dataclass:
  - Test instantiation with all fields
  - Test field types and validation
- Test `SonarQubeMetrics` dataclass:
  - Test instantiation with all fields
  - Test field types and validation

### Step 9: Run tests and verify 100% coverage
- Execute `pytest tests/test_sonarqube.py -v` to run all tests
- Execute `pytest tests/test_sonarqube.py --cov=adws/adw_modules/sonarqube --cov-report=term-missing` to check coverage
- Review coverage report to identify any missed lines
- Add additional test cases for any uncovered code paths
- Re-run tests until 100% coverage is achieved

### Step 10: Validate with full test suite
- Run all tests with `pytest tests/ -v` to ensure no regressions
- Verify all new tests pass
- Confirm no existing tests are broken
- Check that code follows existing test patterns and conventions

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/test_sonarqube.py -v` - Run the new SonarQube tests to validate they all pass
- `pytest tests/test_sonarqube.py --cov=adws/adw_modules/sonarqube --cov-report=term-missing` - Verify 100% coverage of the SonarQube module
- `pytest tests/ -v` - Run full test suite to validate zero regressions across all tests

## Notes
- The SonarQube module uses the `requests` library which must be mocked in tests to avoid real API calls
- Environment variables (SONARQUBE_URL, SONARQUBE_TOKEN, SONARQUBE_PROJECT_KEY) should be mocked using `unittest.mock.patch` or `monkeypatch` fixture
- The module has defensive error handling for missing requests library, failed API calls, and invalid data - all paths must be tested
- The `BaseModel` import from `rococo.models` may need to be mocked if it has dependencies
- Follow the existing test patterns in `tests/test_decorators.py` and other test files for consistency
- Use descriptive test method names following the pattern `test_<method>_<scenario>`
- Group related tests using test classes (e.g., `TestSonarQubeClient`, `TestCoverageFile`)
- The `# NOSONAR` comment pattern from conftest.py should be used for any test credential strings
