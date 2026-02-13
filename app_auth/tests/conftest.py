import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from app_auth.api.utils import create_username


@pytest.fixture
def user(db):
    email = "user@example.com"
    username = create_username(email)
    password = "securepassword!"

    return get_user_model().objects.create_user(
        username=username, email=email, password=password, is_active=True
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    url = reverse("login")
    api_client.post(
        url, {"email": user.email, "password": "securepassword!"}, format="json"
    )

    return api_client
