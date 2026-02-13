import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_login_success(api_client, user):
    url = reverse('login')
    data = {
        "email": user.email,
        "password": "securepassword!",
    }

    response = api_client.post(url, data, format='json')
    response_data = response.json()

    assert response.status_code == 200, f"Login fehlgeschlagen: {response.data}"

    assert "user" in response_data
    assert response_data["user"]["email"] == user.email
    assert "id" in response_data["user"]
