import pytest
from django.urls import reverse
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from django.conf import settings


@pytest.mark.django_db
def test_user_logout_success(authenticated_client, user):

    url = reverse("logout")
    data = {}

    refresh_token_entry = OutstandingToken.objects.filter(user=user).last()
    assert refresh_token_entry is not None

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == 200, f"Logout fehlgeschlagen: {response.data}"
    assert response.cookies["access_token"].value == ""
    assert response.cookies["access_token"]["max-age"] == 0
    assert (
        response.cookies["access_token"]["expires"] == "Thu, 01 Jan 1970 00:00:00 GMT"
    )

    assert response.cookies["refresh_token"].value == ""
    assert response.cookies["refresh_token"]["max-age"] == 0

    assert BlacklistedToken.objects.filter(token=refresh_token_entry).exists()


@pytest.mark.django_db
def test_logout_unauthorized(api_client):
    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == 400
    assert response.data["detail"] == "Refresh-Token required."


@pytest.mark.django_db
def test_logout_with_invalid_jwt_format(api_client):
    url = reverse("logout")
    api_client.cookies["refresh_token"] = "not-a-valid-jwt-string"

    response = api_client.post(url)

    assert response.status_code == 200
    assert response.cookies["refresh_token"].value == ""


@pytest.mark.django_db
def test_logout_with_already_blacklisted_token(authenticated_client, user):
    url = reverse("logout")

    refresh_token = authenticated_client.cookies.get("refresh_token").value

    authenticated_client.post(url)

    authenticated_client.cookies["refresh_token"] = refresh_token

    response = authenticated_client.post(url)

    assert response.status_code == 200
    assert (
        response.data["detail"]
        == "Logout successful! All tokens will be deleted. Refresh token is now invalid."
    )
