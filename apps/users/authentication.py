from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import AuthenticationFailed

class CookiesJWTAuthentication(JWTAuthentication):
    """
    Authenticate using JWT in HttpOnly cookies with CSRF check.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None

        # CSRF check for unsafe methods
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            csrf_token_cookie = request.COOKIES.get('csrf_token')
            csrf_token_header = request.headers.get('X-CSRFToken')
            if csrf_token_cookie != csrf_token_header:
                raise AuthenticationFailed("CSRF verification failed.")

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except TokenError as e:
            raise AuthenticationFailed("Invalid or expired JWT") from e
