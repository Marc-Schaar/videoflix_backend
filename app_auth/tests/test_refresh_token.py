import pytest
from django.urls import reverse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


@pytest.mark.django_db
def test_token_refresh_success(api_client, user):
    url = reverse("token-refresh")

    refresh = RefreshToken.for_user(user)
    refresh_token_str = str(refresh)

    api_client.cookies["refresh_token"] = refresh_token_str

    response = api_client.post(url, {}, format="json")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["detail"] == "Token refreshed"
    assert "access" in response_data

    access_cookie_name = settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token")

    assert (
        access_cookie_name in response.cookies
    ), "Access-Token-Cookie wurde nicht gesetzt"
    assert response.cookies[access_cookie_name].value == response_data["access"]
    assert response.cookies[access_cookie_name]["httponly"] is True


@pytest.mark.django_db
def test_token_refresh_fails_without_cookie(api_client):
    url = reverse("token-refresh")

    response = api_client.post(url, {}, format="json")

    assert response.status_code == 400
    assert response.data["detail"] == "Refresh-Token required."


@pytest.mark.django_db
def test_token_refresh_clears_cookies_on_invalid_token(api_client):
    url = reverse("token-refresh")

    api_client.cookies["refresh_token"] = "completely-invalid-token"

    response = api_client.post(url, {}, format="json")

    assert response.status_code == 401
    assert response.cookies["refresh_token"].value == ""
    assert response.cookies["refresh_token"]["max-age"] == 0
    access_cookie = settings.SIMPLE_JWT["AUTH_COOKIE"]
    assert response.cookies[access_cookie].value == ""


@pytest.mark.django_db
def test_token_refresh_fails_with_expired_token(api_client, user):
    url = reverse("token-refresh")

    refresh = RefreshToken.for_user(user)
    token_str = str(refresh)

    refresh.blacklist()

    api_client.cookies["refresh_token"] = token_str
    response = api_client.post(url, {}, format="json")

    assert response.status_code == 401


def test_token_refresh_rotates_and_blacklists(api_client, user):
    url = reverse("token-refresh")

    refresh = RefreshToken.for_user(user)
    old_refresh_str = str(refresh)
    api_client.cookies["refresh_token"] = old_refresh_str

    response = api_client.post(url, {}, format="json")

    assert response.status_code == 200

    new_refresh_str = response.cookies["refresh_token"].value
    assert new_refresh_str != old_refresh_str

    old_token_entry = OutstandingToken.objects.filter(token=old_refresh_str).first()
    assert BlacklistedToken.objects.filter(
        token=old_token_entry
    ).exists(), "Alter Token wurde nicht geblacklisted!"
