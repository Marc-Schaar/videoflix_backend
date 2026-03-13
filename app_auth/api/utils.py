import uuid
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response


from app_auth.models import User


def create_username(email):
    base_username = email.split("@")[0]
    base_username = base_username[:130]
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{base_username}_{unique_suffix}"


def get_auth_response_data(user, token):
    """Strukturiert die Response-Daten für Registrierung und Login einheitlich."""
    return {
        "user": {
            "id": user.id,
            "email": user.email,
        },
        "token": token,
    }


def generate_auth_tokens(user):
    """Generiert uidb64 und token für Aktivierung oder Passwort-Reset."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


def set_auth_cookies(response, access_token, refresh_token=None):
    """Hilfsmethode zum Setzen der JWT-Cookies."""
    cookie_settings = {
        "httponly": settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        "secure": settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        "samesite": settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    }

    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        **cookie_settings,
    )

    if refresh_token:
        response.set_cookie(key="refresh_token", value=refresh_token, **cookie_settings)

    return response


def delete_auth_cookies(response):
    """Löscht alle authentifizierungsrelevanten Cookies."""
    response.delete_cookie(settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"))
    response.delete_cookie("refresh_token")
    return response


def blacklist_refresh_token(request):
    """Versucht das Refresh-Token aus den Cookies zu blacklisten."""
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            pass 
    return False


def get_error_response():
    """Gibt eine 401 Response zurück und löscht die Cookies."""
    response = Response(
        {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
    )
    response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
    response.delete_cookie("refresh_token")
    return response


def get_user_from_uidb64(uidb64):
    """Versucht einen User anhand der uidb64 zu finden."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None
