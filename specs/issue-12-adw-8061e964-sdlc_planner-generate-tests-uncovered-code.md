# Chore: Generate tests for uncovered code in adw_plan_build_test_iso.py

## Metadata
issue_number: `12`
adw_id: `8061e964`
issue_json: `{"number": 12, "title": "Generate tests for uncovered code", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Create comprehensive unit tests for the `adw_plan_build_test_iso.py` script to achieve 100% code coverage. This script orchestrates three workflow steps (planning, building, and testing) by calling three separate Python scripts in sequence. The tests need to cover all code paths including:
- Successful execution of all three steps
- Failure scenarios in each step
- ADW ID extraction from state files when not provided
- Command-line argument parsing and validation
- Error handling and exit codes

## Relevant Files
Use these files to resolve the chore:

- `/Users/Bek/Downloads/rococo-sample-backend/adws/adw_plan_build_test_iso.py` - The target file that needs test coverage. This script orchestrates the plan-build-test workflow by calling three separate scripts sequentially.

- `/Users/Bek/Downloads/rococo-sample-backend/adws/adw_modules/state.py` - Contains the `ADWState` class used by the target script for loading state from files. Tests need to mock this module's functionality.

- `/Users/Bek/Downloads/rococo-sample-backend/adws/adw_tests/test_agents.py` - Example test file showing the testing patterns used in the adws directory, including how to set up tests, use fixtures, and structure test cases.

- `/Users/Bek/Downloads/rococo-sample-backend/tests/conftest.py` - Contains shared pytest fixtures for the main test suite. Can be referenced for testing patterns and fixture setup.

### New Files

- `/Users/Bek/Downloads/rococo-sample-backend/adws/adw_tests/test_adw_plan_build_test_iso.py` - New test file to be created with comprehensive test coverage for all code paths in adw_plan_build_test_iso.py.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Analyze the target script and identify test scenarios
- Read and understand the complete functionality of `adw_plan_build_test_iso.py`
- Identify all code paths that need test coverage:
  - Main entry point with valid arguments (issue_number only)
  - Main entry point with valid arguments (issue_number and adw_id)
  - Main entry point with missing arguments (should fail)
  - Successful execution of all three steps (plan, build, test)
  - Failure in Step 1 (planning)
  - Failure in Step 2 (building)
  - Failure in Step 3 (testing - non-zero exit code but continues)
  - ADW ID extraction from state files when not provided
  - ADW ID extraction failure when state file not found
  - Environment variable loading via dotenv
- Document edge cases and error conditions

### Step 2: Create comprehensive unit tests
- Create new test file at `/Users/Bek/Downloads/rococo-sample-backend/adws/adw_tests/test_adw_plan_build_test_iso.py`
- Import necessary testing libraries (pytest, unittest.mock, etc.)
- Set up fixtures for:
  - Mocking subprocess.run for the three script calls
  - Mocking file system operations (os.path.exists, os.listdir, etc.)
  - Mocking state file loading
  - Creating temporary directories and files for testing
- Write test cases covering all identified scenarios:
  - `test_main_success_with_adw_id` - Tests successful execution when adw_id is provided
  - `test_main_success_without_adw_id` - Tests successful execution with ADW ID extracted from state
  - `test_main_missing_arguments` - Tests failure when issue_number is not provided
  - `test_main_planning_failure` - Tests failure when Step 1 (planning) fails
  - `test_main_building_failure` - Tests failure when Step 2 (building) fails
  - `test_main_testing_failure` - Tests when Step 3 (testing) returns non-zero exit code
  - `test_main_adw_id_extraction_failure` - Tests failure when ADW ID cannot be extracted from state
  - `test_main_no_state_files` - Tests failure when no state files exist in agents directory
  - `test_main_empty_agents_directory` - Tests when agents directory is empty
  - `test_main_invalid_state_json` - Tests handling of corrupted state JSON files
- Use proper mocking to isolate the script from external dependencies (subprocess, file I/O)
- Ensure each test verifies expected outputs (print statements, exit codes)
- Add docstrings to each test explaining what is being tested

### Step 3: Verify test coverage reaches 100%
- Run pytest with coverage reporting for the target file:
  - `pytest adws/adw_tests/test_adw_plan_build_test_iso.py --cov=adws/adw_plan_build_test_iso --cov-report=term-missing -v`
- Review coverage report to identify any missed lines or branches
- Add additional tests if any code paths are not covered
- Ensure all edge cases are tested

### Step 4: Run validation commands
- Execute all validation commands listed in the `Validation Commands` section
- Verify all tests pass with no failures
- Confirm 100% code coverage is achieved
- Fix any issues found during validation

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest adws/adw_tests/test_adw_plan_build_test_iso.py -v` - Run the new tests to ensure they pass
- `pytest adws/adw_tests/test_adw_plan_build_test_iso.py --cov=adws/adw_plan_build_test_iso --cov-report=term-missing` - Verify 100% code coverage for the target file
- `pytest tests/ -v` - Run all existing tests to ensure no regressions
- `uv run adws/adw_tests/health_check.py` - Run ADW health check to ensure the system still works correctly

## Notes
- The target script uses `subprocess.run()` to call three separate scripts, so tests must mock subprocess to avoid actually running those scripts
- ADW ID extraction logic (lines 48-83) involves reading JSON state files from the `agents/` directory - this complex logic needs thorough testing with various scenarios
- The script prints output with emoji symbols (✅, ❌, ⚠️) - tests should verify these are printed correctly
- Exit codes matter: the script exits with code 1 on failures, but continues with a warning for test failures (Step 3)
- The script uses `sys.argv` for argument parsing, so tests need to mock this
- Environment variables are loaded via `load_dotenv()` - ensure tests don't depend on actual .env files
- Follow the testing patterns established in `adws/adw_tests/test_agents.py` for consistency
- Use pytest's `capsys` fixture to capture and verify stdout/stderr output
- Use `unittest.mock.patch` to mock external dependencies (subprocess, os, file operations)
