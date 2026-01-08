# Chore: Generate tests for adw_plan_build_test_iso.py

## Metadata
issue_number: `5`
adw_id: `0f0d5720`
issue_json: `{"number": 5, "title": "Generate tests", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Generate comprehensive unit tests for the `adw_plan_build_test_iso.py` script to achieve 100% code coverage. This script is a compositional workflow orchestrator that runs three ADW workflows in sequence: planning (adw_plan_iso.py), building (adw_build_iso.py), and testing (adw_test_iso.py). The tests should cover all code paths including successful execution, error handling, ADW ID extraction logic, and edge cases.

The script contains:
- Main entry point function that validates arguments
- Sequential subprocess execution for three workflow phases
- ADW ID extraction logic from state files when not provided
- Error handling and exit code management
- User-friendly console output formatting

## Relevant Files
Use these files to resolve the chore:

- **adws/adw_plan_build_test_iso.py** (Target file requiring tests)
  - Main script that orchestrates plan → build → test workflows
  - Contains main() function with argument parsing, subprocess execution, and error handling
  - Includes logic to extract ADW ID from state files when not provided

- **tests/conftest.py** (Existing test fixtures)
  - Contains shared pytest fixtures (mock_config, app_context, etc.)
  - Provides environment setup for tests
  - Reference for understanding existing test patterns

- **tests/test_decorators.py** (Example test file)
  - Reference for understanding project's testing patterns
  - Shows how mocking and assertions are structured

- **adws/adw_modules/state.py** (State management module)
  - Defines ADWState class used for loading/saving workflow state
  - Referenced by adw_plan_build_test_iso.py for ADW ID extraction

- **adws/README.md** (Documentation)
  - Explains ADW workflow architecture
  - Documents how compositional workflows work
  - Provides context on worktree and state management

### New Files

- **tests/adws/__init__.py**
  - Initialize tests/adws package for ADW-related tests

- **tests/adws/test_adw_plan_build_test_iso.py**
  - Comprehensive unit tests for adw_plan_build_test_iso.py
  - Test all functions, code paths, and edge cases
  - Achieve 100% code coverage

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create test directory structure
- Create `tests/adws/` directory if it doesn't exist
- Create `tests/adws/__init__.py` to make it a Python package

### Step 2: Analyze target script structure
- Review `adws/adw_plan_build_test_iso.py` to understand:
  - Command-line argument parsing logic
  - Subprocess execution patterns
  - ADW ID extraction algorithm from state files
  - Error handling and exit code behavior
  - Console output formatting
- Identify all code paths that need test coverage:
  - Missing issue number argument
  - Planning step success/failure
  - ADW ID extraction from state files (success/failure cases)
  - Building step success/failure
  - Testing step success/failure/warnings
  - Different exit code scenarios

### Step 3: Study existing test patterns
- Review `tests/conftest.py` to understand:
  - Available fixtures
  - Environment setup patterns
  - Mocking strategies
- Review `tests/test_*.py` files to understand:
  - Test structure and naming conventions
  - Assertion patterns
  - Use of unittest.mock

### Step 4: Write comprehensive tests
Create `tests/adws/test_adw_plan_build_test_iso.py` with test coverage for:

**Test Cases to Implement:**

1. **Test argument validation**
   - Test missing issue number (expects sys.exit(1))
   - Test with only issue number (ADW ID extracted from state)
   - Test with both issue number and ADW ID provided

2. **Test main() success path**
   - Mock subprocess.run to return success (returncode=0)
   - Mock all three workflow steps succeeding
   - Verify correct subprocess commands are called
   - Verify success message is printed

3. **Test planning step failure**
   - Mock subprocess.run for plan step to return non-zero exit code
   - Verify script exits with code 1
   - Verify error message is printed

4. **Test ADW ID extraction logic**
   - Mock os.path.exists for agents directory
   - Mock os.listdir to return agent IDs
   - Mock file reading to return state JSON with matching issue number
   - Verify ADW ID is correctly extracted from newest matching state file
   - Test case where no matching state file exists (should exit with error)
   - Test case where agents directory doesn't exist (should exit with error)
   - Test case where state files are malformed JSON (should skip and continue)

5. **Test building step failure**
   - Mock planning step success
   - Mock building step to return non-zero exit code
   - Verify script exits with code 1
   - Verify error message is printed

6. **Test testing step warning scenario**
   - Mock planning and building steps success
   - Mock testing step to return non-zero exit code
   - Verify script does NOT exit (continues to completion)
   - Verify warning message is printed

7. **Test testing step success**
   - Mock all three steps succeeding
   - Verify all success messages are printed
   - Verify final success message is printed

8. **Test environment loading**
   - Verify load_dotenv() is called
   - Test with environment variables set

9. **Test script directory path handling**
   - Verify SCRIPT_DIR is correctly calculated
   - Verify correct paths are constructed for subprocess calls

10. **Test state file sorting and selection**
    - Mock multiple state files with different modification times
    - Verify newest state file is selected first
    - Test case with multiple matching issue numbers (should select newest)

**Testing Strategy:**
- Use `unittest.mock.patch` to mock:
  - `subprocess.run`
  - `sys.argv`
  - `sys.exit`
  - `os.path.exists`, `os.listdir`, `os.path.getmtime`
  - `builtins.open` for file operations
  - `json.load`
  - `dotenv.load_dotenv`
  - `print` to verify console output
- Use `pytest.raises` for exception testing
- Assert on:
  - Subprocess command arguments
  - Exit codes
  - Print statements (error and success messages)
  - File operations (state file reading)
  - Control flow (which steps are executed)

### Step 5: Run tests and verify coverage
- Run `pytest tests/adws/test_adw_plan_build_test_iso.py -v` to ensure all tests pass
- Run `pytest --cov=adws.adw_plan_build_test_iso --cov-report=term-missing tests/adws/test_adw_plan_build_test_iso.py` to verify 100% coverage
- If coverage is below 100%, identify uncovered lines and add missing tests
- Repeat until 100% coverage is achieved

### Step 6: Validate test quality
- Verify all tests follow project conventions
- Ensure tests are isolated and don't depend on external state
- Verify mock objects are properly configured
- Check that assertions are meaningful and test actual behavior
- Ensure test names clearly describe what is being tested

### Step 7: Run full test suite
Execute the validation commands to ensure no regressions and confirm 100% coverage

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/adws/test_adw_plan_build_test_iso.py -v` - Run the new tests to verify they all pass
- `pytest --cov=adws.adw_plan_build_test_iso --cov-report=term-missing tests/adws/test_adw_plan_build_test_iso.py` - Verify 100% coverage for adw_plan_build_test_iso.py
- `pytest tests/ -v` - Run all tests to validate no regressions

## Notes
- The `adw_plan_build_test_iso.py` script is a compositional workflow that runs multiple subprocesses in sequence
- The ADW ID extraction logic is critical: it reads state files from `agents/<adw_id>/adw_state.json` to find the most recent workflow for the given issue number
- The script has different exit behavior for test failures (warning) vs plan/build failures (exit with error)
- All subprocess calls use `sys.executable` to ensure correct Python interpreter
- State files are sorted by modification time (newest first) before matching on issue number
- The script uses dotenv for environment variable loading
- Tests should mock all external dependencies (filesystem, subprocess, environment)
- Aim for 100% line coverage, including error paths and edge cases
