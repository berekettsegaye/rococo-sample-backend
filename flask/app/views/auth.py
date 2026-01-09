from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import get_success_response, get_failure_response, parse_request_body, validate_required_fields
from app.helpers.decorators import login_required
from common.app_config import config
from common.services import AuthService, PersonService, OAuthClient

# Create the auth blueprint
auth_api = Namespace('auth', description="Auth related APIs")


@auth_api.route('/test')
class Test(Resource):
    def get(self):
        login_data = {
            "username": "test",
            "password": "test"
        }
        return get_success_response(**login_data)


@auth_api.route('/signup')
class Signup(Resource):
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'first_name': {'type': 'string'},
            'last_name': {'type': 'string'},
            'email_address': {'type': 'string'}
        }}
    )
    def post(self):
        parsed_body = parse_request_body(request, ['first_name', 'last_name', 'email_address'])
        validate_required_fields(parsed_body)

        auth_service = AuthService(config)

        auth_service.signup(
            parsed_body['email_address'],
            parsed_body['first_name'],
            parsed_body['last_name']
        )
        return get_success_response(message="User signed up successfully and verification email is sent.")


@auth_api.route('/login')
class Login(Resource):
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'email': {'type': 'string'},
            'password': {'type': 'string'},
            'two_factor_code': {'type': 'string'}
        }}
    )
    def post(self):
        parsed_body = parse_request_body(request, ['email', 'password', 'two_factor_code'])
        # Only email and password are required, two_factor_code is optional
        validate_required_fields({'email': parsed_body.get('email'), 'password': parsed_body.get('password')})

        auth_service = AuthService(config)

        try:
            access_token, expiry = auth_service.login_user_by_email_password(
                parsed_body['email'],
                parsed_body['password'],
                parsed_body.get('two_factor_code')
            )

            person_service = PersonService(config)
            person = person_service.get_person_by_email_address(email_address=parsed_body['email'])

            return get_success_response(person=person.as_dict(), access_token=access_token, expiry=expiry)
        except Exception as e:
            # Check if 2FA is required
            if hasattr(e, 'two_factor_required') and e.two_factor_required:
                return get_failure_response(message=str(e), two_factor_required=True)
            raise


@auth_api.route('/forgot_password', doc=dict(description="Send reset password link"))
class ForgotPassword(Resource):
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'email': {'type': 'string'}
        }}
    )
    def post(self):
        parsed_body = parse_request_body(request, ['email'])
        validate_required_fields(parsed_body)

        auth_service = AuthService(config)
        auth_service.trigger_forgot_password_email(parsed_body.get('email'))

        return get_success_response(message="Password reset email sent successfully.")


@auth_api.route(
    '/reset_password/<string:token>/<string:uidb64>',
    doc=dict(description="Update the password using reset password link")
)
class ResetPassword(Resource):
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'password': {'type': 'string'}
        }}
    )
    def post(self, token, uidb64):
        parsed_body = parse_request_body(request, ['password'])
        validate_required_fields(parsed_body)

        auth_service = AuthService(config)
        access_token, expiry, person_obj = auth_service.reset_user_password(token, uidb64, parsed_body.get('password'))
        return get_success_response(
            message="Your password has been updated!", 
            access_token=access_token, 
            expiry=expiry,
            person=person_obj.as_dict()
        )


@auth_api.route('/<string:provider>/exchange')
class OAuthExchange(Resource):
    def post(self, provider):
        """
        Exchange OAuth authorization code for access token and user info
        
        Args:
            provider: OAuth provider (google, microsoft)
        """
        parsed_body = parse_request_body(
            request,
            ['code', 'redirect_uri', 'code_verifier']
        )
        validate_required_fields(parsed_body)

        oauth_client = OAuthClient(config)
        auth_service = AuthService(config)

        try:
            # Token exchange + user info retrieval
            if provider == "google":
                token_response = oauth_client.get_google_token(
                    parsed_body['code'],
                    parsed_body['redirect_uri'],
                    parsed_body['code_verifier']
                )
                user_info = oauth_client.get_google_user_info(token_response['access_token'])

            elif provider == "microsoft":
                token_response = oauth_client.get_microsoft_token(
                    parsed_body['code'],
                    parsed_body['redirect_uri'],
                    parsed_body['code_verifier']
                )
                user_info = oauth_client.get_microsoft_user_info(token_response['access_token'])

            else:
                return get_failure_response(message=f"Unsupported provider: {provider}")

            # Normalize name + email (same structure for both google and microsoft)
            email = user_info.get('email')
            name = user_info.get('name', '')

            if not email:
                return get_failure_response(message=f"{provider.capitalize()} user info does not contain email.")

            name_parts = name.split(' ', 1)
            first_name, last_name = name_parts[0], name_parts[1] if len(name_parts) > 1 else ""

            # Login or create user
            access_token, expiry, person = auth_service.login_user_by_oauth(
                email, first_name, last_name,
                provider=provider,
                provider_data=user_info
            )

            return get_success_response(person=person.as_dict(), access_token=access_token, expiry=expiry)

        except Exception as e:
            return get_failure_response(message=f"OAuth authentication failed: {str(e)}")


@auth_api.route('/2fa/setup')
class TwoFactorSetup(Resource):
    @login_required()
    @auth_api.expect(
        {'type': 'object', 'properties': {}}
    )
    def post(self, person):
        """
        Initiate two-factor authentication setup.
        Returns QR code and backup codes for user to save.

        Args:
            person: Current authenticated user (injected by login_required decorator)
        """
        person_service = PersonService(config)
        email_obj = person_service.get_primary_email_by_person_id(person.entity_id)

        if not email_obj:
            return get_failure_response(message="Email not found for user.")

        auth_service = AuthService(config)
        setup_data = auth_service.setup_two_factor(email_obj.email)

        return get_success_response(
            message="Two-factor authentication setup initiated. Scan the QR code with your authenticator app.",
            secret=setup_data['secret'],
            qr_code=setup_data['qr_code_base64'],
            backup_codes=setup_data['backup_codes']
        )


@auth_api.route('/2fa/verify-and-enable')
class TwoFactorVerifyAndEnable(Resource):
    @login_required()
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'code': {'type': 'string'}
        }}
    )
    def post(self, person):
        """
        Verify TOTP code and enable two-factor authentication.

        Args:
            person: Current authenticated user (injected by login_required decorator)
        """
        parsed_body = parse_request_body(request, ['code'])
        validate_required_fields(parsed_body)

        person_service = PersonService(config)
        email_obj = person_service.get_primary_email_by_person_id(person.entity_id)

        if not email_obj:
            return get_failure_response(message="Email not found for user.")

        auth_service = AuthService(config)
        result = auth_service.verify_and_enable_two_factor(email_obj.email, parsed_body['code'])

        return get_success_response(
            message="Two-factor authentication enabled successfully.",
            backup_codes=result['backup_codes']
        )


@auth_api.route('/2fa/disable')
class TwoFactorDisable(Resource):
    @login_required()
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'password': {'type': 'string'}
        }}
    )
    def post(self, person):
        """
        Disable two-factor authentication with password confirmation.

        Args:
            person: Current authenticated user (injected by login_required decorator)
        """
        parsed_body = parse_request_body(request, ['password'])
        validate_required_fields(parsed_body)

        person_service = PersonService(config)
        email_obj = person_service.get_primary_email_by_person_id(person.entity_id)

        if not email_obj:
            return get_failure_response(message="Email not found for user.")

        auth_service = AuthService(config)
        auth_service.disable_two_factor_for_user(email_obj.email, parsed_body['password'])

        return get_success_response(message="Two-factor authentication disabled successfully.")


@auth_api.route('/2fa/regenerate-backup-codes')
class TwoFactorRegenerateBackupCodes(Resource):
    @login_required()
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'code': {'type': 'string'}
        }}
    )
    def post(self, person):
        """
        Regenerate backup codes for two-factor authentication.

        Args:
            person: Current authenticated user (injected by login_required decorator)
        """
        parsed_body = parse_request_body(request, ['code'])
        validate_required_fields(parsed_body)

        person_service = PersonService(config)
        email_obj = person_service.get_primary_email_by_person_id(person.entity_id)

        if not email_obj:
            return get_failure_response(message="Email not found for user.")

        auth_service = AuthService(config)
        result = auth_service.regenerate_backup_codes_for_user(email_obj.email, parsed_body['code'])

        return get_success_response(
            message="Backup codes regenerated successfully.",
            backup_codes=result['backup_codes']
        )


@auth_api.route('/2fa/status')
class TwoFactorStatus(Resource):
    @login_required()
    def get(self, person):
        """
        Get two-factor authentication status for the current user.

        Args:
            person: Current authenticated user (injected by login_required decorator)
        """
        person_service = PersonService(config)
        email_obj = person_service.get_primary_email_by_person_id(person.entity_id)

        if not email_obj:
            return get_failure_response(message="Email not found for user.")

        from common.services import LoginMethodService
        login_method_service = LoginMethodService(config)
        login_method = login_method_service.get_login_method_by_email_id(email_obj.entity_id)

        if not login_method:
            return get_failure_response(message="Login method not found for user.")

        return get_success_response(
            two_factor_enabled=login_method.has_two_factor_enabled
        )


@auth_api.route('/logout')
class Logout(Resource):
    @login_required()
    def post(self, person):
        """
        Logout user - log the event and return success
        
        Args:
            person: Current authenticated user (injected by login_required decorator)
        """
        try:
            # Log the logout attempt
            if person and hasattr(person, 'first_name') and hasattr(person, 'last_name'):
                print(f"User {person.first_name} {person.last_name} (ID: {person.entity_id}) logged out")
            else:
                print("User logged out (person details not available)")
            
            # Note: Frontend will clear local data and redirect
            # JWT tokens will naturally expire based on their expiry time
            
            return get_success_response(message="Logged out successfully")
            
        except Exception as e:
            # Even if there's an error, return success to not block frontend logout
            print(f"Logout endpoint error (non-blocking): {e}")
            return get_success_response(message="Logged out successfully")
