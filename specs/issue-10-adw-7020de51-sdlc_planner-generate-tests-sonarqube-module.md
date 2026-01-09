# Chore: Generate tests for uncovered code

## Metadata
issue_number: `10`
adw_id: `7020de51`
issue_json: `{"number": 10, "title": "Generate tests for uncovered code", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Generate comprehensive test coverage for the `adws/adw_modules/sonarqube.py` file to reach 100% code coverage. This file contains the SonarQube API integration for fetching code coverage data, including the `SonarQubeClient` class and related data models (`CoverageFile` and `SonarQubeMetrics`).

Currently, the `adws/adw_modules/sonarqube.py` file has no test coverage. This chore involves creating a comprehensive test suite that covers all classes, methods, and edge cases including:
- SonarQubeClient initialization and configuration
- API request handling and error scenarios
- Coverage metrics parsing
- File coverage data retrieval
- Project-wide coverage analysis
- Error handling for various failure scenarios (authentication, network, parsing errors)

## Relevant Files
Use these files to resolve the chore:

- `adws/adw_modules/sonarqube.py` (305 lines) - The main SonarQube integration module that needs test coverage. Contains:
  - `CoverageFile` dataclass for file-level coverage data
  - `SonarQubeMetrics` dataclass for project-level metrics
  - `SonarQubeClient` class with methods for API interaction, coverage retrieval, and data parsing

- `tests/conftest.py` (86 lines) - Test fixtures and configuration. Can be referenced for patterns on:
  - Setting up mock objects and fixtures
  - Database and Flask application testing setup
  - Common testing utilities

- `pyproject.toml` (19 lines) - Pytest and coverage configuration showing:
  - Test paths and Python path configuration
  - Coverage settings and source directories

### New Files
- `tests/test_sonarqube.py` - New comprehensive test file for the SonarQube module covering all functionality

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Analyze the SonarQube module structure
- Read and understand the `adws/adw_modules/sonarqube.py` file thoroughly
- Identify all classes, methods, and code paths that need testing
- Map out edge cases, error scenarios, and success paths
- Note dependencies on external libraries (requests, rococo.models)

### Step 2: Create comprehensive test file for SonarQube module
- Create `tests/test_sonarqube.py` with proper structure and imports
- Set up test fixtures for mocking SonarQube API responses
- Implement test classes for each component:
  - `TestCoverageFile` - Test the CoverageFile dataclass
  - `TestSonarQubeMetrics` - Test the SonarQubeMetrics dataclass
  - `TestSonarQubeClient` - Test initialization and configuration
  - `TestSonarQubeClientMakeRequest` - Test API request handling
  - `TestSonarQubeClientGetProjectMetrics` - Test project metrics retrieval
  - `TestSonarQubeClientGetFileCoverage` - Test file coverage retrieval
  - `TestSonarQubeClientGetAllFiles` - Test file listing
  - `TestSonarQubeClientGetUncoveredFiles` - Test uncovered file discovery
  - `TestSonarQubeClientGetCoverageSummary` - Test coverage summary generation
  - `TestSonarQubeClientGetUncoveredFilesSummary` - Test uncovered files summary

### Step 3: Implement tests for all success scenarios
- Test successful initialization with environment variables
- Test successful initialization with explicit parameters
- Test successful API requests with authentication
- Test successful parsing of metrics data
- Test successful file coverage retrieval with uncovered lines
- Test successful project-wide operations
- Ensure all return types and data structures are validated

### Step 4: Implement tests for all error and edge cases
- Test missing environment variables and configuration errors
- Test authentication failures (401 responses)
- Test API not found errors (404 responses)
- Test other API error responses (500, etc.)
- Test network connection errors and timeouts
- Test malformed JSON response handling
- Test missing or invalid data in responses
- Test empty result sets
- Test missing requests library import error
- Test pagination and large result sets (coverage summary limits)

### Step 5: Implement tests for data parsing and validation
- Test correct parsing of SonarQube metrics into dataclasses
- Test handling of missing metric keys
- Test type conversions (string to float/int)
- Test URL construction and parameter formatting
- Test project key prefix handling in file paths
- Test coverage threshold filtering logic

### Step 6: Add mocking and fixtures
- Use unittest.mock to mock requests library and HTTP responses
- Create fixtures for common test data (sample API responses)
- Mock environment variables using monkeypatch
- Create reusable mock response generators for different scenarios

### Step 7: Run tests and verify 100% coverage for SonarQube module
- Execute pytest with coverage reporting for the SonarQube module
- Verify that `adws/adw_modules/sonarqube.py` reaches 100% coverage
- Review coverage report to identify any missed branches or lines
- Add additional tests if any code paths are uncovered

### Step 8: Execute validation commands
- Run the full test suite to ensure no regressions
- Run tests with verbose output to confirm all test cases pass
- Generate coverage report to validate 100% coverage achievement

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/test_sonarqube.py -v` - Run new SonarQube tests with verbose output
- `pytest tests/test_sonarqube.py -v --cov=adws/adw_modules/sonarqube --cov-report=term-missing` - Verify 100% coverage for SonarQube module
- `pytest tests/ -v` - Run all tests to validate no regressions
- `pytest tests/ -v --cov=. --cov-report=term-missing` - Verify overall project coverage remains high

## Notes
- The SonarQube module uses the `requests` library which needs to be mocked in tests to avoid actual HTTP calls
- Pay special attention to authentication handling using HTTPBasicAuth with token
- The module includes both dataclasses (BaseModel) and a client class - test both thoroughly
- Error logging should be tested to ensure proper error messages are generated
- The module has optional dependencies (requests) - test the ImportError path when requests is not available
- Consider testing with various SonarQube API response formats to ensure robustness
- The coverage summary methods have output limiting logic (first 20 files, first 50 lines) that should be tested
- Use pytest fixtures and parametrize decorators to reduce test code duplication where appropriate
