from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response


from app_auth.models import User

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from .services.send_mail import send_activation_mail
from .permissions import HasRefreshTokenCookie
from .utils import create_username


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.username = create_username(user.email)
            if settings.DEBUG:
                user.is_active = True
            else:
                user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            send_activation_mail(user, token, uidb64)

            data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "token": uidb64,
            }

            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateView(APIView):
    permission_class = AllowAny

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data["access"]
        refresh_token = serializer.validated_data["refresh"]

        response = Response(
            {
                "message": "Login successful",
                "user": {"email": serializer.user.email, "id": serializer.user.id},
            },
            status=status.HTTP_200_OK,
        )

        cookie_settings = {
            "httponly": settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            "secure": settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            "samesite": settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        }

        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            **cookie_settings
        )

        response.set_cookie(key="refresh_token", value=refresh_token, **cookie_settings)

        return response


class LogOutView(APIView):
    permission_classes = [HasRefreshTokenCookie]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh-Token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_cookie_name = settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception:
            pass

        response = Response(
            {
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )
        response.delete_cookie(access_cookie_name)
        response.delete_cookie("refresh_token")

        return response


class TokenRefreshView(TokenRefreshView):
    permission_classes = [HasRefreshTokenCookie]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            response= Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )

            response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
            response.delete_cookie("refresh_token")
            return response

        access_token = serializer.validated_data.get("access")
        new_refresh_token = serializer.validated_data.get("refresh")

        response = Response(
            {"detail": "Token refreshed", "access": access_token},
            status=status.HTTP_200_OK,
        )

        cookie_settings = {
            "httponly": settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            "secure": settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            "samesite": settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        }

        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            **cookie_settings
        )

        if new_refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                **cookie_settings
            )

        return response
