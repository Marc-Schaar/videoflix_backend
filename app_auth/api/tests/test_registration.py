import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()


@pytest.mark.django_db
def test_user_registration_success(api_client):
    url = reverse('register')
    data = {
        "email": "user@example.com",
        "password": "securepassword!",
        "confirmed_password": "securepassword!"
    }

    response = api_client.post(url, data, format='json')
    response_data = response.json()

    assert response.status_code == 201, f"Registrierung fehlgeschlagen: {response.data}"
    assert User.objects.filter(email="user@example.com").exists()


    assert "user" in response_data
    assert response_data["user"]["email"] == "user@example.com"
    assert "id" in response_data["user"]


    assert "token" in response_data
    assert response_data["token"] is not None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["user@example.com"]
    assert "Confirm your Email" in mail.outbox[0].subject
