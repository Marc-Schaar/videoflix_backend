import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken



User = get_user_model()


@pytest.mark.django_db
def test_user_login_success(api_client, user):

    url = reverse("login")
    data = {
        "email": user.email,
        "password": "securepassword!",
    }

    response = api_client.post(url, data, format="json")
    response_data = response.json()

    assert response.status_code == 200, f"Login fehlgeschlagen: {response.data}"

    assert "user" in response_data
    assert response_data["user"]["email"] == user.email
    assert "id" in response_data["user"]

    access_cookie_name = settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token')

    assert access_cookie_name in response.cookies, "Access Token Cookie fehlt"
    assert "refresh_token" in response.cookies, "Refresh Token Cookie fehlt"

    assert response.cookies[access_cookie_name]['httponly'] is True

    token_value = response.cookies[access_cookie_name].value
    decoded_token = AccessToken(token_value)

    user_id_claim = settings.SIMPLE_JWT.get('USER_ID_CLAIM', 'user_id')
    assert decoded_token[user_id_claim] == user.email


@pytest.mark.django_db
def test_login_wrong_password(api_client, user):
    url = reverse("login")
    data = {
        "email": user.email,
        "password": "definitely-not-the-right-password",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "Inavlid Email or Password" in str(response.data)
    assert settings.SIMPLE_JWT['AUTH_COOKIE'] not in response.cookies


@pytest.mark.django_db
def test_login_email_does_not_exist(api_client):
    url = reverse("login")
    data = {
        "email": "ghost@example.com",
        "password": "anypassword",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "Inavlid Email or Password" in str(response.data)


@pytest.mark.django_db
def test_login_user_inactive(api_client, user, settings):
    user.is_active = False
    user.save()

    url = reverse("login")
    data = {
        "email": user.email,
        "password": "securepassword!",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "Authentication failed. Please verify your account." in str(response.data)
