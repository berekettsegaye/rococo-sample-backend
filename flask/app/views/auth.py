from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import get_success_response, get_failure_response, parse_request_body, validate_required_fields
from app.helpers.decorators import login_required
from common.app_config import config
from common.services import AuthService, PersonService, OAuthClient, TotpService

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
            'totp_code': {'type': 'string'}
        }}
    )
    def post(self):
        parsed_body = parse_request_body(request, ['email', 'password', 'totp_code'])

        # Only email and password are required initially
        if not parsed_body.get('email') or not parsed_body.get('password'):
            return get_failure_response(message="Email and password are required.")

        auth_service = AuthService(config)
        person_service = PersonService(config)

        # Get person first to check 2FA status
        person = person_service.get_person_by_email_address(email_address=parsed_body['email'])

        if not person:
            # Try to authenticate to give proper error message
            try:
                auth_service.login_user_by_email_password(
                    parsed_body['email'],
                    parsed_body['password']
                )
            except Exception as e:
                return get_failure_response(message=str(e))

        # Check if 2FA is enabled for this user
        if person and person.is_2fa_enabled:
            totp_code = parsed_body.get('totp_code')

            # If 2FA is enabled but no TOTP code provided
            if not totp_code:
                return get_success_response(
                    requires_2fa=True,
                    message="2FA is enabled. Please provide your TOTP code."
                )

            # Verify TOTP code
            totp_service = TotpService(config)
            try:
                if not totp_service.verify_2fa_code(person, totp_code):
                    return get_failure_response(message="Invalid TOTP code. Please try again.")
            except Exception as e:
                return get_failure_response(message=str(e))

        # Proceed with normal login (password has been validated implicitly by getting here)
        try:
            access_token, expiry = auth_service.login_user_by_email_password(
                parsed_body['email'],
                parsed_body['password']
            )

            return get_success_response(
                person=person.as_dict(),
                access_token=access_token,
                expiry=expiry
            )
        except Exception as e:
            return get_failure_response(message=str(e))


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


@auth_api.route('/2fa/enable')
class Enable2FA(Resource):
    @login_required()
    def post(self, person):
        """
        Enable 2FA by generating a TOTP secret and QR code.

        Args:
            person: Current authenticated user (injected by login_required decorator)

        Returns:
            JSON with secret, qr_code (base64), and backup_codes (empty for now)
        """
        try:
            totp_service = TotpService(config)
            secret, qr_code, uri = totp_service.enable_2fa(person)

            return get_success_response(
                message="2FA setup initiated. Please scan the QR code with your authenticator app.",
                secret=secret,
                qr_code=qr_code,
                backup_codes=[]  # Future enhancement
            )
        except Exception as e:
            return get_failure_response(message=str(e))


@auth_api.route('/2fa/confirm')
class Confirm2FA(Resource):
    @login_required()
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'secret': {'type': 'string'},
            'code': {'type': 'string'}
        }}
    )
    def post(self, person):
        """
        Confirm and activate 2FA by verifying a TOTP code.

        Args:
            person: Current authenticated user (injected by login_required decorator)

        Request body:
            secret: The TOTP secret from the enable endpoint
            code: The 6-digit TOTP code from authenticator app
        """
        try:
            parsed_body = parse_request_body(request, ['secret', 'code'])
            validate_required_fields(parsed_body)

            totp_service = TotpService(config)
            updated_person = totp_service.confirm_enable_2fa(
                person,
                parsed_body['secret'],
                parsed_body['code']
            )

            return get_success_response(
                message="2FA has been successfully enabled for your account.",
                is_2fa_enabled=updated_person.is_2fa_enabled
            )
        except Exception as e:
            return get_failure_response(message=str(e))


@auth_api.route('/2fa/disable')
class Disable2FA(Resource):
    @login_required()
    @auth_api.expect(
        {'type': 'object', 'properties': {
            'password': {'type': 'string'}
        }}
    )
    def post(self, person):
        """
        Disable 2FA for a user after verifying their password.

        Args:
            person: Current authenticated user (injected by login_required decorator)

        Request body:
            password: The user's password for verification
        """
        try:
            parsed_body = parse_request_body(request, ['password'])
            validate_required_fields(parsed_body)

            totp_service = TotpService(config)
            updated_person = totp_service.disable_2fa(person, parsed_body['password'])

            return get_success_response(
                message="2FA has been disabled for your account.",
                is_2fa_enabled=updated_person.is_2fa_enabled
            )
        except Exception as e:
            return get_failure_response(message=str(e))


@auth_api.route('/2fa/status')
class TwoFactorStatus(Resource):
    @login_required()
    def get(self, person):
        """
        Get 2FA status for the current user.

        Args:
            person: Current authenticated user (injected by login_required decorator)

        Returns:
            JSON with is_2fa_enabled and has_totp_secret flags
        """
        try:
            totp_service = TotpService(config)
            status = totp_service.get_2fa_status(person)

            return get_success_response(**status)
        except Exception as e:
            return get_failure_response(message=str(e))
