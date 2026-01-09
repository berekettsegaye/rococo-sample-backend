# Chore: Generate test for uncovered code

## Metadata
issue_number: `18`
adw_id: `9b0b6f40`
issue_json: `{"number": 18, "title": "Generate test for uncovered code", "body": "Generate test for uncovered code. the test coverage must reach 100%."}`

## Chore Description
Generate comprehensive unit tests for all uncovered code in the rococo-sample-backend project to achieve 100% test coverage. The project currently has some tests for decorators, factory, login_method, response, version, and person_org_role_service, but many files in the `common/` directory lack complete test coverage. According to `pyproject.toml`, coverage is tracked for:
- `common/models/*`
- `common/repositories/*`
- `common/services/*`
- `common/utils/*`
- `flask/app/helpers/*`

This chore requires identifying all files with less than 100% coverage and creating thorough unit tests that cover all code paths, edge cases, and error scenarios.

## Relevant Files
Use these files to resolve the chore:

### Existing Test Infrastructure
- `tests/conftest.py` - Contains shared pytest fixtures and mock objects (MockPerson, MockEmail, MockOrganization, mock_config, mock_repository fixtures)
- `pyproject.toml` - Defines test configuration, coverage settings, and paths to include in coverage reports

### Existing Tests (Reference Patterns)
- `tests/test_decorators.py` - Tests for flask/app/helpers/decorators.py
- `tests/test_response.py` - Tests for flask/app/helpers/response.py
- `tests/test_factory.py` - Tests for common/repositories/factory.py
- `tests/test_login_method.py` - Tests for common/models/login_method.py
- `tests/test_version.py` - Tests for common/utils/version.py
- `tests/test_person_org_role_service.py` - Tests for common/services/person_organization_role.py

### Files Requiring Test Coverage

#### common/models/
- `common/models/email.py` - Email model with validate_email method (regex validation, length checks, error handling)
- `common/models/organization.py` - Organization model (simple base class extension)
- `common/models/person.py` - Person model with type checking enabled
- `common/models/person_organization_role.py` - PersonOrganizationRole model (simple base class extension)

#### common/repositories/
- `common/repositories/base.py` - BaseRepository with MODEL validation in __init_subclass__
- `common/repositories/email.py` - EmailRepository extending BaseRepository
- `common/repositories/organization.py` - OrganizationRepository with get_organizations_by_person_id method
- `common/repositories/person.py` - PersonRepository extending BaseRepository
- `common/repositories/person_organization_role.py` - PersonOrganizationRoleRepository extending BaseRepository

#### common/services/
- `common/services/auth.py` - AuthService with signup, login, OAuth, password reset methods (most complex service)
- `common/services/email.py` - EmailService with save_email, get_email_by_email_address, verify_email methods
- `common/services/oauth.py` - OAuthClient with Google and Microsoft OAuth token/userinfo methods
- `common/services/organization.py` - OrganizationService with save, get, and get_organizations_with_roles_by_person methods
- `common/services/person.py` - PersonService with save_person, get_person_by_email_address, get_person_by_id methods
- `common/services/login_method.py` - LoginMethodService with save, get_by_email_id, get_by_id, update_password methods

#### common/helpers/
- `common/helpers/auth.py` - JWT token generation and parsing utilities (generate_access_token, parse_access_token, create_person_from_token, create_email_from_token)
- `common/helpers/string_utils.py` - String encoding/decoding utilities (urlsafe_base64_encode/decode, force_str, force_bytes, is_protected_type)
- `common/helpers/exceptions.py` - Custom exception classes

#### common/utils/
- `common/utils/version.py` - Already has tests in test_version.py, may need additional coverage for edge cases

### New Files
#### tests/test_email_model.py
- Tests for Email model validation logic

#### tests/test_organization_model.py
- Tests for Organization model

#### tests/test_person_model.py
- Tests for Person model

#### tests/test_person_org_role_model.py
- Tests for PersonOrganizationRole model

#### tests/test_base_repository.py
- Tests for BaseRepository including MODEL validation

#### tests/test_email_repository.py
- Tests for EmailRepository

#### tests/test_organization_repository.py
- Tests for OrganizationRepository including get_organizations_by_person_id

#### tests/test_person_repository.py
- Tests for PersonRepository

#### tests/test_person_org_role_repository.py
- Tests for PersonOrganizationRoleRepository

#### tests/test_auth_service.py
- Comprehensive tests for AuthService covering all methods and error paths

#### tests/test_email_service.py
- Tests for EmailService

#### tests/test_oauth_service.py
- Tests for OAuthClient including mocked HTTP requests

#### tests/test_organization_service.py
- Tests for OrganizationService

#### tests/test_person_service.py
- Tests for PersonService

#### tests/test_login_method_service.py
- Tests for LoginMethodService

#### tests/test_auth_helpers.py
- Tests for common/helpers/auth.py JWT utilities

#### tests/test_string_utils.py
- Tests for common/helpers/string_utils.py encoding/decoding utilities

#### tests/test_exceptions.py
- Tests for common/helpers/exceptions.py custom exceptions

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Analyze Current Coverage
- Run pytest with coverage to identify uncovered lines in each module
- Generate a coverage report to see which files and lines are missing tests
- Document the baseline coverage percentage before starting
- Prioritize files with lowest coverage first

### Step 2: Create Tests for common/models/
- Create `tests/test_email_model.py` with tests for:
  - Valid email validation
  - Invalid email format (missing @, invalid domain)
  - Email address exceeding 254 characters
  - Non-string email addresses
  - Multiple validation errors at once
- Create `tests/test_organization_model.py` with basic instantiation tests
- Create `tests/test_person_model.py` with tests for:
  - Person instantiation with type checking enabled
  - Type checking validation
- Create `tests/test_person_org_role_model.py` with basic instantiation tests

### Step 3: Create Tests for common/repositories/
- Create `tests/test_base_repository.py` with tests for:
  - Successful instantiation with valid MODEL attribute
  - TypeError when MODEL is None in subclass
  - Proper initialization with db_adapter, message_adapter, queue_name, user_id
- Create `tests/test_email_repository.py` with tests for:
  - Repository instantiation with correct MODEL
  - Verify MODEL is set to Email class
- Create `tests/test_organization_repository.py` with tests for:
  - Repository instantiation
  - get_organizations_by_person_id method with valid person_id
  - get_organizations_by_person_id with empty results
- Create `tests/test_person_repository.py` with basic repository tests
- Create `tests/test_person_org_role_repository.py` with basic repository tests

### Step 4: Create Tests for common/services/ (Part 1 - Simple Services)
- Create `tests/test_email_service.py` with tests for:
  - save_email method
  - get_email_by_email_address with existing/non-existing email
  - get_email_by_id with valid/invalid entity_id
  - verify_email method
- Create `tests/test_login_method_service.py` with tests for:
  - save_login_method
  - get_login_method_by_email_id with existing/non-existing email_id
  - get_login_method_by_id with valid/invalid entity_id
  - update_password method
- Create `tests/test_person_service.py` with tests for:
  - save_person method
  - get_person_by_email_address with existing/non-existing email
  - get_person_by_id with valid/invalid entity_id
  - get_person_by_email_address when email exists but person doesn't
- Create `tests/test_organization_service.py` with tests for:
  - save_organization method
  - get_organization_by_id with valid/invalid entity_id
  - get_organizations_with_roles_by_person method

### Step 5: Create Tests for common/services/ (Part 2 - OAuth Service)
- Create `tests/test_oauth_service.py` with tests for:
  - get_google_token with valid code (mock successful response)
  - get_google_token with invalid code (mock 400/401 error)
  - get_google_token with network error (mock RequestException)
  - get_google_user_info with valid token
  - get_google_user_info with invalid token
  - get_microsoft_token with valid code
  - get_microsoft_token with invalid code
  - get_microsoft_user_info with valid token
  - get_microsoft_user_info with userPrincipalName vs mail field handling

### Step 6: Create Tests for common/services/ (Part 3 - Auth Service)
- Create `tests/test_auth_service.py` with comprehensive tests for:
  - signup with new user (success case)
  - signup with existing email (OAuth conflict case)
  - signup with existing email (non-OAuth case)
  - login_user_by_email_password with valid credentials
  - login_user_by_email_password with invalid email
  - login_user_by_email_password with incorrect password
  - login_user_by_email_password on OAuth account (should fail)
  - login_user_by_email_password with no password set
  - login_user_by_oauth for new user (Google)
  - login_user_by_oauth for existing user (Microsoft)
  - login_user_by_oauth for existing user without login_method (edge case)
  - login_user_by_oauth for non-OAuth account conversion
  - generate_reset_password_token
  - prepare_password_reset_url
  - send_welcome_email
  - parse_reset_password_token with valid token
  - parse_reset_password_token with expired token
  - trigger_forgot_password_email with valid email
  - trigger_forgot_password_email with invalid email
  - send_password_reset_email
  - reset_user_password with valid token
  - reset_user_password with invalid token
  - reset_user_password with invalid uidb64

### Step 7: Create Tests for common/helpers/
- Create `tests/test_auth_helpers.py` with tests for:
  - generate_access_token with login_method, person, and email
  - generate_access_token with login_method only (minimal payload)
  - generate_access_token with login_method and person but no email
  - parse_access_token with valid non-expired token
  - parse_access_token with expired token
  - parse_access_token with invalid token
  - create_person_from_token with full token data
  - create_person_from_token with minimal token data
  - create_email_from_token with full token data
  - create_email_from_token with minimal token data
- Create `tests/test_string_utils.py` with tests for:
  - normal_url_safe_b64_decode with valid input
  - normal_url_safe_b64_encode with valid input
  - is_protected_type with None, int, float, Decimal, datetime, date, time
  - is_protected_type with non-protected types (str, list, dict)
  - urlsafe_base64_encode with bytestring
  - urlsafe_base64_decode with valid encoded string
  - urlsafe_base64_decode with invalid string (ValueError)
  - force_str with string input
  - force_str with bytes input
  - force_str with strings_only=True and protected type
  - force_str with non-string input
  - force_bytes with bytes input
  - force_bytes with string input
  - force_bytes with memoryview input
  - force_bytes with strings_only=True and protected type
  - force_bytes with different encoding
- Create `tests/test_exceptions.py` with tests for:
  - InputValidationError instantiation and message
  - APIException instantiation and message

### Step 8: Run Coverage Analysis
- Execute `pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml` to generate detailed coverage report
- Review coverage report to identify any remaining uncovered lines
- Calculate overall coverage percentage
- Identify specific lines that are still uncovered

### Step 9: Add Missing Edge Case Tests
- Review coverage report line-by-line for each module
- Add tests for any uncovered branches, exception handlers, or edge cases
- Focus on error paths that may have been missed
- Test all conditional branches (if/else, try/except)
- Ensure all return paths are tested

### Step 10: Verify 100% Coverage Achievement
- Run final coverage analysis: `pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml`
- Confirm all files in pyproject.toml include list have 100% coverage
- Document any intentionally uncovered code with # pragma: no cover if justified
- Generate final coverage.xml report for SonarQube integration

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/ -v` - Run all tests to ensure they pass without errors
- `pytest tests/ -v --cov=. --cov-report=term-missing` - Generate coverage report showing all covered lines
- `pytest tests/ -v --cov=. --cov-report=xml --cov-report=term` - Generate XML coverage report for CI/CD integration
- `pytest tests/test_email_model.py -v` - Verify Email model tests pass
- `pytest tests/test_base_repository.py -v` - Verify BaseRepository tests pass
- `pytest tests/test_auth_service.py -v` - Verify AuthService tests pass (most complex)
- `pytest tests/test_oauth_service.py -v` - Verify OAuthClient tests pass
- `pytest tests/test_auth_helpers.py -v` - Verify auth helper tests pass
- `pytest tests/test_string_utils.py -v` - Verify string_utils tests pass

## Notes
- All tests should follow the existing patterns in `tests/conftest.py` using mock fixtures
- Use `@patch` decorator from `unittest.mock` for mocking external dependencies (HTTP requests, database calls)
- Ensure tests are isolated and don't depend on external services (PostgreSQL, RabbitMQ)
- Use the existing `mock_config`, `mock_repository`, `mock_person`, `mock_email`, `mock_organization` fixtures
- For services that use RepositoryFactory, mock the factory to return mock repositories
- For OAuthClient tests, use `@patch('requests.post')` and `@patch('requests.get')` to mock HTTP calls
- For AuthService tests, mock all service dependencies (PersonService, EmailService, LoginMethodService, etc.)
- Add `# NOSONAR` comments for test data that might trigger security scanners (e.g., hardcoded test passwords)
- Consider adding `# pragma: no cover` only for defensive code that can't be tested (e.g., ImportError handlers for optional dependencies)
- The coverage threshold is 100% - any file with less than 100% coverage should be addressed
- Focus on testing business logic and edge cases, not just achieving coverage metrics
- All tests must pass independently and not rely on test execution order
