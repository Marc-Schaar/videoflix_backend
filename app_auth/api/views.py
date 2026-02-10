from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from rest_framework.response import Response

from app_auth.models import User

from .serializers import RegistrationSerializer
from .services.send_mail import sendActivationMail

class RegisterView(APIView):
    permission_class= AllowAny

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        username = request.data.get("username")
        email = request.data.get("email")

        if User.objects.filter(username=username).exists():
            return Response(
                {"username": "A user with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"email": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            sendActivationMail(user, token, uidb64)

            data = {
               "user" :user,
               "token": uidb64

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
            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
