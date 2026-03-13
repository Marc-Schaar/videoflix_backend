# Nur noch das Nötigste in der views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    RegistrationSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
)
from .services.send_mail import send_activation_mail, send_password_reset_mail
from .permissions import HasRefreshTokenCookie
from .utils import (
    set_auth_cookies,
    get_error_response,
    get_auth_response_data,
    get_user_from_uidb64,
    generate_auth_tokens,
    delete_auth_cookies,
    blacklist_refresh_token,
)
from .messages import AuthMessages

User = get_user_model()

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        uidb64, token = generate_auth_tokens(user)

        transaction.on_commit(
            lambda: send_activation_mail.delay(user.id, token, uidb64)
        )

        data = get_auth_response_data(user, token)

        return Response(data, status=status.HTTP_201_CREATED)


class ActivateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, uidb64, token):
        user = get_user_from_uidb64(uidb64)

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {"error": AuthMessages.INVALID_TOKEN},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()
        return Response(
            {"message": AuthMessages.ACTIVATION_SUCCESS},
            status=status.HTTP_200_OK,
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
                "detail": AuthMessages.LOGIN_SUCCESS,
                "user": {"email": serializer.user.email, "id": serializer.user.id},
            },
            status=status.HTTP_200_OK,
        )

        return set_auth_cookies(response, access_token, refresh_token)


class LogOutView(APIView):
    permission_classes = [HasRefreshTokenCookie]
    authentication_classes = []

    def post(self, request):
        blacklist_refresh_token(request)

        response = Response(
            {"detail": AuthMessages.LOGOUT_SUCCESS},
            status=status.HTTP_200_OK,
        )

        return delete_auth_cookies(response)


class TokenRefreshView(TokenRefreshView):
    permission_classes = [HasRefreshTokenCookie]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return get_error_response()

        access_token = serializer.validated_data.get("access")
        new_refresh_token = serializer.validated_data.get("refresh")

        response = Response(
            {"detail": AuthMessages.TOKEN_REFRESH_SUCCESS, "access": access_token},
            status=status.HTTP_200_OK,
        )
        return set_auth_cookies(response, access_token, new_refresh_token)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            uidb64, token = generate_auth_tokens(user)

            transaction.on_commit(
                lambda: send_password_reset_mail.delay(user.id, token, uidb64)
            )

        return Response(
            {"detail": AuthMessages.PW_RESET_SENT},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        user = get_user_from_uidb64(uidb64)

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {"error": AuthMessages.INVALID_PW_LINK},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": AuthMessages.PW_RESET_SUCCESS},
            status=status.HTTP_200_OK,
        )
