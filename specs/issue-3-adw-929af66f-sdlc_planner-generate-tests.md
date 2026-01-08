# Chore: Generate Tests

## Metadata
issue_number: `3`
adw_id: `929af66f`
issue_json: `{"number": 3, "title": "Generate Tests", "body": "adw_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%. "}`

## Chore Description
Generate comprehensive unit tests for all uncovered code in the `adw_test_iso.py` script to achieve 100% test coverage. This chore focuses on creating tests for the ADW Test Iso workflow script, which is responsible for running tests in isolated worktrees, generating tests for uncovered code using SonarQube coverage data, and auto-resolving test failures.

The `adw_test_iso.py` script is a critical component of the AI Developer Workflow (ADW) system. It orchestrates the testing phase by:
- Running pytest test suites in isolated worktree environments
- Fetching SonarQube coverage data to identify uncovered code
- Generating tests using Claude Code's `/test` command
- Auto-resolving test failures through multiple retry attempts
- Committing and pushing test results
- Posting results to GitHub issues

This chore requires analyzing the existing code, identifying all untested functions and code paths, and creating comprehensive unit tests following the project's testing patterns and best practices.

## Relevant Files
Use these files to resolve the chore:

- `/Users/Bek/Downloads/rococo-sample-backend/adws/adw_test_iso.py` - Main target file to generate tests for. Contains the core workflow logic for isolated testing.
- `/Users/Bek/Downloads/rococo-sample-backend/trees/929af66f/tests/conftest.py` - Shared pytest fixtures and test configuration. Provides examples of mock objects and test setup patterns used in the project.
- `/Users/Bek/Downloads/rococo-sample-backend/trees/929af66f/tests/test_factory.py` - Example test file demonstrating the project's testing patterns, including mocking, patching, and test structure.
- `/Users/Bek/Downloads/rococo-sample-backend/trees/929af66f/pyproject.toml` - Contains pytest configuration and coverage settings.
- `/Users/Bek/Downloads/rococo-sample-backend/adws/README.md` - ADW system documentation providing context on how `adw_test_iso.py` fits into the overall workflow.

### New Files
- `/Users/Bek/Downloads/rococo-sample-backend/adws/tests/test_adw_test_iso.py` - New test file containing comprehensive unit tests for `adw_test_iso.py`.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Analyze adw_test_iso.py and Identify Coverage Gaps
- Read and analyze the entire `adw_test_iso.py` file to understand its functionality
- Identify all functions, methods, and code paths that need test coverage:
  - `run_tests()` - Function that executes the /test command with SonarQube coverage data
  - `run_pytest()` - Function that runs pytest with sys.executable
  - `parse_test_results()` - Function that parses JSON test results
  - `format_test_results_comment()` - Function that formats test results for GitHub comments
  - `resolve_failed_tests()` - Function that attempts to resolve test failures
  - `main()` - Main entry point with complex workflow orchestration
  - Error handling paths and edge cases throughout
- Document the dependencies and imports used (dotenv, subprocess, sys, os, logging, etc.)
- Review how the script interacts with ADW modules (agent, github, state, git_ops, sonarqube, error_handling, preflight)

### Step 2: Review Existing Test Patterns
- Study `tests/conftest.py` to understand available fixtures and test setup patterns
- Analyze `tests/test_factory.py` to learn the project's testing conventions:
  - How to structure test classes
  - How to use mocks and patches effectively
  - How to write descriptive test names and docstrings
  - How to test error conditions
- Identify reusable patterns for mocking external dependencies (subprocess, file I/O, API calls)

### Step 3: Design Test Suite Structure
- Plan test classes and test methods to cover all functions:
  - `TestRunTests` - Tests for the `run_tests()` function
  - `TestRunPytest` - Tests for the `run_pytest()` function
  - `TestParseTestResults` - Tests for the `parse_test_results()` function
  - `TestFormatTestResultsComment` - Tests for the `format_test_results_comment()` function
  - `TestResolveFailedTests` - Tests for the `resolve_failed_tests()` function
  - `TestMain` - Tests for the `main()` function covering the entire workflow
- Identify edge cases and error conditions to test:
  - Missing state files
  - Invalid worktree paths
  - Pytest execution failures
  - JSON parsing errors
  - SonarQube API failures
  - GitHub API failures
  - Test retry logic
- Plan fixtures needed for testing (mocked dependencies, sample data, etc.)

### Step 4: Create Test Fixtures and Mock Helpers
- Create the new test file at `adws/tests/test_adw_test_iso.py`
- Add necessary imports (pytest, unittest.mock, MagicMock, patch, etc.)
- Create reusable fixtures for:
  - Mock logger instances
  - Mock ADWState objects
  - Mock AgentPromptResponse objects
  - Mock TestResult objects
  - Sample pytest output strings
  - Sample test results JSON data
- Create helper functions for common mocking patterns (e.g., mocking subprocess.run, mocking file operations)

### Step 5: Implement Tests for Individual Functions
- Write comprehensive tests for `run_tests()`:
  - Test successful test execution with coverage data
  - Test successful test execution without coverage data
  - Test error handling when execute_template fails
  - Verify correct AgentTemplateRequest construction
- Write comprehensive tests for `run_pytest()`:
  - Test successful pytest execution (returncode 0)
  - Test failed pytest execution (returncode != 0)
  - Test subprocess exception handling
  - Verify correct command construction with sys.executable
- Write comprehensive tests for `parse_test_results()`:
  - Test parsing valid JSON with passed tests
  - Test parsing valid JSON with failed tests
  - Test parsing empty results
  - Test error handling for invalid JSON
- Write comprehensive tests for `format_test_results_comment()`:
  - Test formatting with only passed tests
  - Test formatting with only failed tests
  - Test formatting with mixed results
  - Test formatting with empty results
- Write comprehensive tests for `resolve_failed_tests()`:
  - Test resolving with failed tests
  - Test resolving with no failed tests
  - Test error handling in resolve process

### Step 6: Implement Tests for Main Workflow Function
- Write comprehensive tests for `main()` function:
  - Test successful complete workflow execution
  - Test missing command-line arguments
  - Test missing state file (ADWError raised)
  - Test worktree validation failure
  - Test preflight check failures
  - Test SonarQube integration success and fallback
  - Test pytest execution and parsing
  - Test test generation iterations (success after 1st iteration)
  - Test test generation iterations (success after multiple iterations)
  - Test test retry attempts on failures
  - Test commit and finalize operations
  - Test GitHub comment posting
  - Test --skip-e2e flag handling
- Mock all external dependencies:
  - Environment variables (dotenv)
  - System arguments (sys.argv)
  - File system operations
  - Subprocess calls
  - ADW module functions (execute_template, make_issue_comment, etc.)
  - State management (ADWState.load)
  - Git operations (commit_changes, finalize_git_operations)
  - SonarQubeClient methods

### Step 7: Test Edge Cases and Error Conditions
- Add tests for error paths and edge cases:
  - Invalid issue numbers or ADW IDs
  - Network failures (GitHub API, SonarQube API)
  - Disk space issues
  - Permission errors
  - Concurrent execution scenarios
  - Regex parsing failures in pytest output
  - Maximum iteration limits reached
  - Maximum retry attempts reached
- Add tests for boundary conditions:
  - Empty pytest output
  - Very large test result sets
  - Tests with special characters in names
  - Multiple test failure scenarios

### Step 8: Ensure 100% Coverage
- Run pytest with coverage to measure current coverage:
  ```bash
  pytest adws/tests/test_adw_test_iso.py --cov=adws/adw_test_iso --cov-report=term-missing
  ```
- Identify any remaining uncovered lines or branches
- Add additional tests to cover any gaps:
  - Uncovered conditional branches (if/else)
  - Uncovered exception handlers
  - Uncovered loop iterations
  - Uncovered return paths
- Verify 100% coverage is achieved for `adw_test_iso.py`

### Step 9: Run Validation Commands
- Execute all validation commands to ensure tests are complete and passing
- Verify no regressions in existing tests
- Ensure all new tests follow project conventions

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/ -v` - Run all existing tests to validate no regressions
- `pytest adws/tests/test_adw_test_iso.py -v` - Run new tests for adw_test_iso.py
- `pytest adws/tests/test_adw_test_iso.py --cov=adws/adw_test_iso --cov-report=term-missing` - Verify 100% coverage for adw_test_iso.py
- `pytest adws/tests/ -v` - Run all ADW tests if there are other test files in the adws/tests directory

## Notes
- The `adw_test_iso.py` script uses the uv package manager, so tests should be run with `uv run` if needed
- The script depends heavily on ADW modules (`adw_modules.*`), which should be mocked in tests
- The script uses `sys.executable -m pytest` to run pytest, ensuring it uses the correct Python interpreter
- The script has complex iteration and retry logic (MAX_TEST_GENERATION_ITERATIONS, MAX_TEST_RETRY_ATTEMPTS) that needs thorough testing
- The script interacts with external services (GitHub, SonarQube), which should be mocked to avoid real API calls
- The script uses subprocess for git operations and pytest execution, which should be mocked
- Pay attention to the state management (ADWState) and worktree validation logic
- The script has specific error handling using ADWError and safe_execute patterns
- Test the regex parsing logic for pytest output carefully, as it extracts test counts
- Consider testing the commit message formatting and git operations
- The script supports a `--skip-e2e` flag that should be tested
- Follow the existing test patterns in the project (test classes, descriptive names, docstrings, mocks)
