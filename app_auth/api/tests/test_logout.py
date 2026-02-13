import pytest
from django.urls import reverse
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


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

    assert response.cookies["refresh_token"].value == ""
    assert response.cookies["refresh_token"]["max-age"] == 0

    assert BlacklistedToken.objects.filter(token=refresh_token_entry).exists()
