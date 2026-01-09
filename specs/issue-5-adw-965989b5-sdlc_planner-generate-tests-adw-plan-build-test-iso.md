# Chore: Generate tests for adw_plan_build_test_iso.py

## Metadata
issue_number: `5`
adw_id: `965989b5`
issue_json: `{"number":5,"title":"Generate tests","body":"adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Generate comprehensive test suite for the `adw_plan_build_test_iso.py` script to achieve 100% code coverage. This script orchestrates the ADW workflow by coordinating planning (adw_plan_iso.py), building (adw_build_iso.py), and testing (adw_test_iso.py) phases. The tests must cover all execution paths including success scenarios, error conditions, edge cases, and subprocess failures.

## Relevant Files
Use these files to resolve the chore:

- `/Users/Bek/Desktop/tac-8/tac8_app5__nlq_to_sql_aea/rococo-sample-backend/adws/adw_plan_build_test_iso.py` - The primary file requiring test coverage. This script is a workflow orchestrator that:
  - Accepts issue number and optional ADW ID as command-line arguments
  - Executes three sequential subprocess calls (plan, build, test)
  - Extracts ADW ID from state files when not provided
  - Handles subprocess failures and provides appropriate exit codes
  - Uses environment variables loaded via dotenv

- `/Users/Bek/Desktop/tac-8/tac8_app5__nlq_to_sql_aea/rococo-sample-backend/adws/adw_modules/state.py` - ADW state management module that the target script uses to find ADW IDs from state files. Understanding this helps mock state file lookups.

- `/Users/Bek/Desktop/tac-8/tac8_app5__nlq_to_sql_aea/rococo-sample-backend/adws/adw_modules/data_types.py` - Contains ADWStateData and related data structures that the state module uses.

- `/Users/Bek/Desktop/tac-8/tac8_app5__nlq_to_sql_aea/rococo-sample-backend/tests/conftest.py` - Existing pytest fixtures and test configuration that should be reused for consistency.

### New Files

- `/Users/Bek/Desktop/tac-8/tac8_app5__nlq_to_sql_aea/rococo-sample-backend/tests/test_adw_plan_build_test_iso.py` - New test file that will contain comprehensive test cases covering all functionality, error paths, and edge cases for the adw_plan_build_test_iso.py script.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Analyze the target script structure
- Read and understand adw_plan_build_test_iso.py:112
  - Entry point and argument parsing (lines 28-33)
  - Step 1: Planning subprocess execution (lines 35-46)
  - ADW ID extraction logic from state files (lines 48-83)
  - Step 2: Building subprocess execution (lines 85-94)
  - Step 3: Testing subprocess execution (lines 96-107)
  - Main function and script entry point (lines 110-111)
- Identify all code paths requiring coverage:
  - Success path with ADW ID provided
  - Success path without ADW ID (must extract from state)
  - Planning subprocess failure
  - Building subprocess failure
  - Testing subprocess failure with warnings
  - No state file found after planning
  - Invalid command-line arguments
  - File system errors when reading state files

### 2. Create comprehensive test suite structure
- Create `/Users/Bek/Desktop/tac-8/tac8_app5__nlq_to_sql_aea/rococo-sample-backend/tests/test_adw_plan_build_test_iso.py`
- Import required testing libraries:
  - pytest for test framework
  - unittest.mock for mocking subprocess calls, file system operations, and sys.argv
  - sys, os for path and argument manipulation
  - json for state file mocking
- Structure test class(es) with logical grouping:
  - Test class for main() function behavior
  - Test class for ADW ID extraction logic
  - Test class for subprocess execution paths
  - Test class for error handling

### 3. Implement test cases for command-line argument handling
- Test with insufficient arguments (sys.argv with only script name)
  - Should exit with code 1
  - Should print usage message
- Test with issue number only (sys.argv with 2 elements)
  - Should proceed with ADW ID extraction
- Test with both issue number and ADW ID (sys.argv with 3 elements)
  - Should skip ADW ID extraction
  - Should use provided ADW ID

### 4. Implement test cases for successful execution paths
- Test complete workflow with ADW ID provided:
  - Mock subprocess.run for all three steps (plan, build, test) to return success (returncode=0)
  - Mock load_dotenv
  - Verify all three subprocess calls are made with correct arguments
  - Verify success message is printed
- Test complete workflow without ADW ID:
  - Mock subprocess.run for all three steps
  - Mock file system to simulate state file exists with matching issue number
  - Mock os.path.exists, os.listdir, os.path.getmtime, and file open
  - Verify ADW ID is extracted correctly
  - Verify subsequent steps use extracted ADW ID

### 5. Implement test cases for subprocess failure scenarios
- Test planning step failure:
  - Mock subprocess.run for plan step to return failure (returncode!=0)
  - Verify script exits with code 1
  - Verify build and test steps are not executed
- Test building step failure:
  - Mock subprocess.run: plan succeeds, build fails
  - Verify script exits with code 1
  - Verify test step is not executed
- Test testing step failure with warnings:
  - Mock subprocess.run: plan and build succeed, test fails
  - Verify warning message is printed
  - Verify script does not exit with error (continues)

### 6. Implement test cases for ADW ID extraction edge cases
- Test when no state files exist:
  - Mock agents directory to be empty or nonexistent
  - Verify error message about not finding ADW ID
  - Verify script exits with code 1
- Test when state files exist but none match the issue number:
  - Mock multiple state files with different issue numbers
  - Verify script exits with error
- Test when state file has invalid JSON:
  - Mock state file with JSONDecodeError on read
  - Verify script handles error gracefully and continues searching
- Test when state file exists but has no issue_number key:
  - Mock state file with valid JSON but missing issue_number
  - Verify script handles KeyError and continues searching
- Test with multiple state files, correct one is newest:
  - Mock multiple state files with different modification times
  - Verify script selects the newest matching state file

### 7. Implement test cases for path and directory handling
- Test SCRIPT_DIR calculation:
  - Verify script uses correct directory for finding other ADW scripts
- Test state file path construction:
  - Mock various directory structures
  - Verify correct path to agents/{adw_id}/adw_state.json
- Test worktree path handling:
  - Verify script correctly passes paths to subprocess calls

### 8. Add integration-style test cases
- Test with realistic mock data:
  - Use actual ADW ID format (8 characters)
  - Use realistic issue numbers
  - Mock complete state file JSON structure matching ADWStateData
- Test environment variable loading:
  - Mock load_dotenv behavior
  - Verify dotenv is called early in execution

### 9. Ensure 100% code coverage
- Run pytest with coverage:
  - `pytest tests/test_adw_plan_build_test_iso.py -v --cov=adws/adw_plan_build_test_iso --cov-report=term-missing`
- Review coverage report and identify any uncovered lines
- Add additional test cases for any missing coverage:
  - Exception handling blocks
  - Edge cases in conditional logic
  - Print statements (verify they are called)
- Re-run coverage until 100% is achieved

### 10. Add test documentation and cleanup
- Add docstrings to all test functions describing:
  - What scenario is being tested
  - Expected behavior
  - What mocks are used
- Add module-level docstring explaining test suite purpose
- Ensure test names follow convention: `test_<scenario>_<expected_behavior>`
- Review and clean up any redundant or duplicate test cases
- Ensure all tests are independent (no shared state between tests)

### 11. Run validation commands
Execute validation commands to ensure the chore is complete with zero regressions.

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/test_adw_plan_build_test_iso.py -v` - Run new test suite and verify all tests pass
- `pytest tests/test_adw_plan_build_test_iso.py -v --cov=adws/adw_plan_build_test_iso --cov-report=term-missing` - Verify 100% code coverage for target file
- `pytest tests/ -v` - Run full test suite to ensure no regressions in existing tests
- `pytest tests/ -v --cov=adws/adw_plan_build_test_iso --cov-report=html` - Generate HTML coverage report for visual verification (optional but recommended)

## Notes
- The target script uses subprocess.run() which must be mocked to avoid executing actual ADW workflows during testing
- State file discovery logic (lines 48-83) is complex and requires careful mocking of file system operations
- The script has multiple exit points (sys.exit) which should be tested by catching SystemExit exceptions
- Use pytest.raises(SystemExit) context manager to test exit scenarios
- Mock sys.argv using monkeypatch fixture or manual patching to test different command-line arguments
- The script imports from adw_modules.state which should be mocked to avoid dependencies on actual state files
- Follow existing test patterns in tests/conftest.py for consistency
- Consider using parameterized tests (pytest.mark.parametrize) for testing multiple similar scenarios
- The script uses print() for user output; use capsys fixture to capture and verify output messages
- Ensure tests are isolated and don't depend on actual file system state or external processes
- The script modifies working directory; ensure tests restore original state using fixtures
