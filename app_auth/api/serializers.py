from django.contrib.auth import get_user_model
from rest_framework import serializers
from app_auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True,)
    confirm_password = serializers.CharField(write_only=True,)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
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
