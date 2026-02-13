from rest_framework.test import APIClient
import pytest

from django.contrib.auth import get_user_model
from utils import create_username


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
