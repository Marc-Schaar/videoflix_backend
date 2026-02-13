import pytest
from django.urls import reverse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_token_refresh_success(api_client, user):
    url = reverse("token_refresh")  

    refresh = RefreshToken.for_user(user)
    refresh_token_str = str(refresh)

    api_client.cookies["refresh_token"] = refresh_token_str

    response = api_client.post(url, {}, format="json")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["detail"] == "Token refreshed"
    assert "access" in response_data
    
    access_cookie_name = settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token')

    assert access_cookie_name in response.cookies, "Access-Token-Cookie wurde nicht gesetzt"
    assert response.cookies[access_cookie_name].value == response_data["access"]
    assert response.cookies[access_cookie_name]['httponly'] is True
