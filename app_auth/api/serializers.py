from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from app_auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import create_username

"""Serializers for authentication-related operations.

This module provides serializers for user registration, password reset, and
custom JWT token handling. They integrate with Django's user model and
SimpleJWT for secure authentication flows.
"""


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for resetting a user's password.

    Validates that the new password and confirmation match. The create method
    is overridden but not typically used in password reset flows.
    """

    new_password = serializers.CharField(
        write_only=True,
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.username = create_username(user.email)
        user.is_active = getattr(settings, "DEBUG", False)
        user.save()
        return user

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration.

    Handles creation of new user accounts with email and password validation.
    Ensures passwords match and email is unique.
    """

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True, "allow_blank": False},
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def save(self):
        pw = self.validated_data["password"]

        account = User(email=self.validated_data["email"])
        account.set_password(pw)
        account.save()
        return account


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that uses email instead of username.

    Extends SimpleJWT's TokenObtainPairSerializer to authenticate via email
    and password, while maintaining compatibility with the standard flow.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Inavlid Email or Password")

        if not user.check_password(password):
            raise serializers.ValidationError("Inavlid Email or Password")

        if not user.is_active:
            raise serializers.ValidationError(
                {"email": "Authentication failed. Please verify your account."}
            )

        data = super().validate({"username": user.username, "password": password})
        return data
    new_password = serializers.CharField(
        write_only=True,
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.username = create_username(user.email)
        user.is_active = getattr(settings, "DEBUG", False)
        user.save()
        return user

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True, "allow_blank": False},
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def save(self):
        pw = self.validated_data["password"]

        account = User(email=self.validated_data["email"])
        account.set_password(pw)
        account.save()
        return account


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Inavlid Email or Password")

        if not user.check_password(password):
            raise serializers.ValidationError("Inavlid Email or Password")

        if not user.is_active:
            raise serializers.ValidationError(
                {"email": "Authentication failed. Please verify your account."}
            )

        data = super().validate({"username": user.username, "password": password})
        return data
