# Chore: Generate test

## Metadata
issue_number: `1`
adw_id: `bd40afd4`
issue_json: `{"number":1,"title":"Generate test","body":"adw_plan_build_test_iso.py\n\nGenerate tests for uncovered code"}`

## Chore Description
Generate comprehensive unit tests for uncovered code in the rococo-sample-backend project. The current test suite covers decorators, factory, version, login method, person organization role service, and response helpers. However, many critical modules lack test coverage, including:

- Common helpers (auth, string_utils, exceptions)
- Service layer (auth, email, oauth, organization, person)
- Repository layer (base, email, organization, person, login_method, person_organization_role)
- Models (all models lack dedicated tests)

This chore will create test files following the existing test patterns in the project to achieve comprehensive coverage of business logic, edge cases, and error handling.

## Relevant Files
Use these files to resolve the chore:

### Existing Test Files (Reference Patterns)
- `tests/conftest.py` - Contains shared fixtures and test configuration. Provides mock objects, config fixtures, and Flask app context setup. Use as reference for creating new fixtures.
- `tests/test_decorators.py` - Tests for flask/app/helpers/decorators.py. Demonstrates comprehensive testing of decorators with mocking.
- `tests/test_factory.py` - Tests for common/repositories/factory.py. Shows patterns for testing repository factory and connection management.
- `tests/test_response.py` - Tests for flask/app/helpers/response.py. Shows testing of response helpers.
- `tests/test_version.py` - Tests for common/utils/version.py. Demonstrates testing utility functions.
- `tests/test_login_method.py` - Tests for login method service. Shows service layer testing patterns.
- `tests/test_person_org_role_service.py` - Tests for person organization role service. Shows service testing with repository mocks.

### Files Requiring Test Coverage (Target Files)

#### Common Helpers (Priority: High)
- `common/helpers/auth.py` - JWT token generation and parsing functions. Critical security functions that need thorough testing for token generation, expiration, parsing, and error handling.
- `common/helpers/string_utils.py` - String encoding/decoding utilities including base64 operations. Need tests for encoding/decoding, edge cases, and error handling.
- `common/helpers/exceptions.py` - Custom exception classes. Need basic tests to ensure exceptions can be raised and caught properly.

#### Services (Priority: High)
- `common/services/auth.py` - Authentication service with signup, login, OAuth, password reset. Complex business logic requiring extensive testing of all auth flows, error cases, and integrations.
- `common/services/email.py` - Email service for CRUD operations. Need tests for save, retrieve, and verify operations with repository mocking.
- `common/services/oauth.py` - OAuth client for Google and Microsoft. Need tests for token exchange, user info retrieval, error handling, and HTTP request mocking.
- `common/services/organization.py` - Organization service. Need tests for CRUD operations and person-organization relationships.
- `common/services/person.py` - Person service. Need tests for CRUD operations and email integration.

#### Repositories (Priority: Medium)
- `common/repositories/base.py` - Base repository with core CRUD operations. Need tests for save, get_one, get_many, and delete operations with database mocking.
- `common/repositories/email.py` - Email repository. Need tests for email-specific queries.
- `common/repositories/organization.py` - Organization repository. Need tests for organization queries and person relationships.
- `common/repositories/person.py` - Person repository. Need tests for person queries.
- `common/repositories/login_method.py` - Login method repository. Need tests for login method queries.
- `common/repositories/person_organization_role.py` - Person organization role repository. Need tests for role queries and relationships.

#### Models (Priority: Medium)
- `common/models/person.py` - Person model. Need tests for initialization, validation, and dataclass behavior.
- `common/models/email.py` - Email model. Need tests for initialization, validation, and email format validation.
- `common/models/organization.py` - Organization model. Need tests for initialization and validation.
- `common/models/login_method.py` - Login method model with password hashing. Need tests for initialization, password hashing, OAuth methods, and validation.
- `common/models/person_organization_role.py` - Person organization role model. Need tests for initialization and role validation.

#### Configuration (Priority: Low)
- `pyproject.toml` - Already configured with pytest settings and coverage configuration. Update if needed to include new test files.

### New Files
#### Test Files to Create
- `tests/test_auth_helpers.py` - Unit tests for common/helpers/auth.py
- `tests/test_string_utils.py` - Unit tests for common/helpers/string_utils.py
- `tests/test_exceptions.py` - Unit tests for common/helpers/exceptions.py
- `tests/test_auth_service.py` - Unit tests for common/services/auth.py
- `tests/test_email_service.py` - Unit tests for common/services/email.py
- `tests/test_oauth_service.py` - Unit tests for common/services/oauth.py
- `tests/test_organization_service.py` - Unit tests for common/services/organization.py
- `tests/test_person_service.py` - Unit tests for common/services/person.py
- `tests/test_base_repository.py` - Unit tests for common/repositories/base.py
- `tests/test_email_repository.py` - Unit tests for common/repositories/email.py
- `tests/test_organization_repository.py` - Unit tests for common/repositories/organization.py
- `tests/test_person_repository.py` - Unit tests for common/repositories/person.py
- `tests/test_login_method_repository.py` - Unit tests for common/repositories/login_method.py
- `tests/test_person_org_role_repository.py` - Unit tests for common/repositories/person_organization_role.py
- `tests/test_person_model.py` - Unit tests for common/models/person.py
- `tests/test_email_model.py` - Unit tests for common/models/email.py
- `tests/test_organization_model.py` - Unit tests for common/models/organization.py
- `tests/test_login_method_model.py` - Unit tests for common/models/login_method.py
- `tests/test_person_org_role_model.py` - Unit tests for common/models/person_organization_role.py

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Tests for Common Helpers (Foundation)
Start with the foundational helper functions as they are dependencies for other modules.

- Create `tests/test_auth_helpers.py` with tests for:
  - `generate_access_token()` - Test with valid login method, person, and email. Verify token structure and expiration.
  - `generate_access_token()` - Test without person and email (optional parameters). Verify basic token payload.
  - `parse_access_token()` - Test with valid token. Verify decoded payload matches.
  - `parse_access_token()` - Test with expired token. Verify returns None.
  - `parse_access_token()` - Test with invalid token. Verify returns None.
  - `create_person_from_token()` - Test with complete token data. Verify Person object created correctly.
  - `create_person_from_token()` - Test with minimal token data. Verify defaults are handled.
  - `create_email_from_token()` - Test with complete token data. Verify Email object created correctly.
  - `create_email_from_token()` - Test with minimal token data. Verify defaults are handled.

- Create `tests/test_string_utils.py` with tests for:
  - `normal_url_safe_b64_decode()` - Test with valid encoded string. Verify correct decoding.
  - `normal_url_safe_b64_encode()` - Test with valid string. Verify correct encoding.
  - `is_protected_type()` - Test with protected types (None, int, float, Decimal, datetime). Verify returns True.
  - `is_protected_type()` - Test with non-protected types (str, list, dict). Verify returns False.
  - `urlsafe_base64_encode()` - Test with bytestring. Verify correct encoding without padding.
  - `urlsafe_base64_decode()` - Test with valid encoded string. Verify correct decoding.
  - `urlsafe_base64_decode()` - Test with invalid string. Verify raises ValueError.
  - `force_str()` - Test with string. Verify returns as-is.
  - `force_str()` - Test with bytes. Verify converts to string.
  - `force_str()` - Test with protected types and strings_only=True. Verify returns as-is.
  - `force_bytes()` - Test with bytes. Verify returns as-is.
  - `force_bytes()` - Test with string. Verify converts to bytes.
  - `force_bytes()` - Test with protected types and strings_only=True. Verify returns as-is.
  - `force_bytes()` - Test with memoryview. Verify converts to bytes.

- Create `tests/test_exceptions.py` with tests for:
  - `InputValidationError` - Test can be raised and caught. Verify message is preserved.
  - `APIException` - Test can be raised and caught. Verify message is preserved.

### Step 2: Create Tests for Models
Test the data models to ensure proper initialization and validation.

- Create `tests/test_person_model.py` with tests for:
  - Person initialization with all fields. Verify fields are set correctly.
  - Person initialization with minimal fields. Verify defaults and entity_id generation.
  - Person with missing required fields (if applicable). Verify validation.

- Create `tests/test_email_model.py` with tests for:
  - Email initialization with all fields. Verify fields are set correctly.
  - Email initialization with minimal fields. Verify defaults and entity_id generation.
  - Email with is_verified flag. Verify default is False.

- Create `tests/test_organization_model.py` with tests for:
  - Organization initialization with name. Verify fields are set correctly.
  - Organization entity_id generation. Verify unique IDs.

- Create `tests/test_login_method_model.py` with tests for:
  - LoginMethod initialization with email/password type. Verify password is hashed.
  - LoginMethod initialization with OAuth type. Verify method_type and method_data.
  - LoginMethod password hashing. Verify raw_password is hashed properly.
  - LoginMethod is_oauth_method property. Verify returns True for OAuth types.
  - LoginMethod oauth_provider_name property. Verify extracts provider name correctly.

- Create `tests/test_person_org_role_model.py` with tests for:
  - PersonOrganizationRole initialization. Verify all fields set correctly.
  - PersonOrganizationRole role validation (if applicable).

### Step 3: Create Tests for Repository Layer
Test the repository layer with mocked database connections.

- Create `tests/test_base_repository.py` with tests for:
  - BaseRepository save() operation. Mock database adapter and verify save is called.
  - BaseRepository get_one() operation. Mock adapter and verify query parameters.
  - BaseRepository get_many() operation. Mock adapter and verify returns list.
  - BaseRepository delete() operation. Mock adapter and verify delete is called.
  - BaseRepository error handling. Mock adapter to raise exception and verify propagation.

- Create `tests/test_email_repository.py` with tests for:
  - EmailRepository inherits from BaseRepository. Verify initialization.
  - EmailRepository specific queries (if any). Mock and verify.

- Create `tests/test_organization_repository.py` with tests for:
  - OrganizationRepository get_organizations_by_person_id(). Mock query and verify results.
  - OrganizationRepository inherits from BaseRepository. Verify initialization.

- Create `tests/test_person_repository.py` with tests for:
  - PersonRepository inherits from BaseRepository. Verify initialization.
  - PersonRepository specific queries (if any). Mock and verify.

- Create `tests/test_login_method_repository.py` with tests for:
  - LoginMethodRepository inherits from BaseRepository. Verify initialization.
  - LoginMethodRepository specific queries (if any). Mock and verify.

- Create `tests/test_person_org_role_repository.py` with tests for:
  - PersonOrganizationRoleRepository inherits from BaseRepository. Verify initialization.
  - PersonOrganizationRoleRepository role-specific queries. Mock and verify.

### Step 4: Create Tests for Service Layer
Test the service layer with mocked repositories and dependencies.

- Create `tests/test_email_service.py` with tests for:
  - EmailService.save_email() - Mock repository and verify save called.
  - EmailService.get_email_by_email_address() - Mock repository and verify query.
  - EmailService.get_email_by_id() - Mock repository and verify query.
  - EmailService.verify_email() - Mock repository, verify is_verified set to True and saved.

- Create `tests/test_person_service.py` with tests for:
  - PersonService.save_person() - Mock repository and verify save called.
  - PersonService.get_person_by_email_address() - Mock email service and person repository. Verify lookup chain.
  - PersonService.get_person_by_id() - Mock repository and verify query.
  - PersonService.get_person_by_email_address() with non-existent email. Verify returns None.

- Create `tests/test_organization_service.py` with tests for:
  - OrganizationService.save_organization() - Mock repository and verify save called.
  - OrganizationService.get_organization_by_id() - Mock repository and verify query.
  - OrganizationService.get_organizations_with_roles_by_person() - Mock repository and verify person_id passed.

- Create `tests/test_oauth_service.py` with tests for:
  - OAuthClient.get_google_token() - Mock requests.post to return token. Verify correct API call and parameters.
  - OAuthClient.get_google_token() with error response. Mock 400 response and verify exception handling.
  - OAuthClient.get_google_user_info() - Mock requests.get to return user info. Verify correct API call and headers.
  - OAuthClient.get_google_user_info() with error response. Verify exception handling.
  - OAuthClient.get_microsoft_token() - Mock requests.post to return token. Verify correct API call and parameters.
  - OAuthClient.get_microsoft_token() with error response. Verify exception handling.
  - OAuthClient.get_microsoft_user_info() - Mock requests.get to return user info. Verify correct transformation.
  - OAuthClient.get_microsoft_user_info() with error response. Verify exception handling.

- Create `tests/test_auth_service.py` with tests for:
  - AuthService.signup() with new user. Mock all service dependencies and verify user creation flow.
  - AuthService.signup() with existing email. Verify raises InputValidationError.
  - AuthService.signup() with existing OAuth email. Verify raises InputValidationError with provider message.
  - AuthService.login_user_by_email_password() with valid credentials. Mock services and verify returns token.
  - AuthService.login_user_by_email_password() with invalid email. Verify raises InputValidationError.
  - AuthService.login_user_by_email_password() with invalid password. Verify raises InputValidationError.
  - AuthService.login_user_by_email_password() for OAuth account. Verify raises InputValidationError with provider message.
  - AuthService.login_user_by_oauth() with new user. Mock services and verify user creation and token generation.
  - AuthService.login_user_by_oauth() with existing user. Mock services and verify token generation.
  - AuthService.login_user_by_oauth() with existing user missing login method. Verify creates OAuth login method.
  - AuthService.generate_reset_password_token() - Mock login method and verify token generation.
  - AuthService.prepare_password_reset_url() - Mock token generation and verify URL format.
  - AuthService.send_welcome_email() - Mock message sender and verify message sent.
  - AuthService.send_password_reset_email() - Mock message sender and verify message sent.
  - AuthService.trigger_forgot_password_email() with valid email. Mock services and verify email sent.
  - AuthService.trigger_forgot_password_email() with non-existent email. Verify raises APIException.
  - AuthService.reset_user_password() with valid token. Mock services and verify password updated and token returned.
  - AuthService.reset_user_password() with invalid token. Verify raises APIException.
  - AuthService.reset_user_password() with expired token. Verify raises APIException.
  - AuthService.parse_reset_password_token() with valid token. Verify returns decoded payload.
  - AuthService.parse_reset_password_token() with expired token. Verify returns None.

### Step 5: Update Test Configuration
Ensure test configuration is optimized for the new tests.

- Review `pyproject.toml` coverage configuration. Verify all new test targets are included in coverage.
- Update coverage include paths if any new directories were added.
- Verify pytest configuration is appropriate for all new test files.

### Step 6: Run Validation Commands
Execute validation commands to ensure all tests pass and coverage is improved.

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/test_auth_helpers.py -v` - Run auth helpers tests
- `pytest tests/test_string_utils.py -v` - Run string utils tests
- `pytest tests/test_exceptions.py -v` - Run exceptions tests
- `pytest tests/test_person_model.py -v` - Run person model tests
- `pytest tests/test_email_model.py -v` - Run email model tests
- `pytest tests/test_organization_model.py -v` - Run organization model tests
- `pytest tests/test_login_method_model.py -v` - Run login method model tests
- `pytest tests/test_person_org_role_model.py -v` - Run person org role model tests
- `pytest tests/test_base_repository.py -v` - Run base repository tests
- `pytest tests/test_email_repository.py -v` - Run email repository tests
- `pytest tests/test_organization_repository.py -v` - Run organization repository tests
- `pytest tests/test_person_repository.py -v` - Run person repository tests
- `pytest tests/test_login_method_repository.py -v` - Run login method repository tests
- `pytest tests/test_person_org_role_repository.py -v` - Run person org role repository tests
- `pytest tests/test_email_service.py -v` - Run email service tests
- `pytest tests/test_person_service.py -v` - Run person service tests
- `pytest tests/test_organization_service.py -v` - Run organization service tests
- `pytest tests/test_oauth_service.py -v` - Run OAuth service tests
- `pytest tests/test_auth_service.py -v` - Run auth service tests
- `pytest tests/ -v` - Run all tests to ensure no regressions
- `pytest tests/ -v --cov=common --cov=flask --cov-report=term-missing` - Run tests with coverage report to verify improved coverage

## Notes

### Testing Patterns to Follow
- All tests should use the existing `conftest.py` fixtures for consistency
- Use `@patch` decorator for mocking external dependencies (repositories, services, HTTP requests)
- Follow the class-based test organization pattern (e.g., `TestLoginRequired`, `TestOrganizationRequired`)
- Test both success paths and error paths for all functions
- For services, mock the repository layer to isolate service logic
- For repositories, mock the database adapter to isolate repository logic
- Use descriptive test names that explain what is being tested (e.g., `test_login_required_success`, `test_login_required_no_auth_header`)

### Key Testing Considerations
- **Auth helpers**: Focus on JWT token generation, parsing, expiration, and error cases
- **String utils**: Focus on encoding/decoding edge cases and error handling
- **Services**: Focus on business logic, error handling, and integration between services
- **Repositories**: Focus on query construction and data mapping
- **Models**: Focus on initialization, validation, and computed properties
- **OAuth**: Mock HTTP requests using `unittest.mock.patch` for `requests.post` and `requests.get`

### Coverage Goals
- Aim for >80% coverage across all target modules
- Prioritize testing critical security functions (auth, password handling)
- Ensure all error paths are tested
- Test edge cases and boundary conditions

### Test Execution Notes
- Tests are isolated and do not require a running database or RabbitMQ
- All external dependencies are mocked using unittest.mock
- Tests use in-memory Flask app context from conftest.py
- Environment variables are set by the `setup_test_env` fixture in conftest.py
