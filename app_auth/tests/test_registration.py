import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()


@pytest.mark.django_db
def test_user_registration_success(api_client, settings):
    settings.RQ_QUEUES["default"]["ASYNC"] = False
    email = "newuser@example.com"
    url = reverse("register")
    data = {
        "email": email,
        "password": "securepassword!",
        "confirmed_password": "securepassword!",
    }

    response = api_client.post(url, data, format="json")
    response_data = response.json()

    assert response.status_code == 201, f"Registrierung fehlgeschlagen: {response.data}"

    from django.contrib.auth import get_user_model

    User = get_user_model()

    assert User.objects.filter(email=email).exists()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [email]

    assert "user" in response_data
    assert response_data["user"]["email"] == email
    assert "id" in response_data["user"]

    assert "token" in response_data
    assert response_data["token"] is not None

    assert len(mail.outbox) == 1
    sent_mail = mail.outbox[0]

    assert "Confirm your Email" in sent_mail.subject


@pytest.mark.django_db
def test_user_registration_password_mismatch(api_client):
    url = reverse("register")
    data = {
        "username": "testuser",
        "email": "wrongpass@example.com",
        "password": "securepassword123!",
        "confirmed_password": "differentpassword!",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "non_field_errors" in response.data or "confirmed_password" in response.data


@pytest.mark.django_db
def test_user_registration_missing_fields(api_client):
    url = reverse("register")
    data = {
        "username": "nonemailuser",
        "password": "securepassword123!",
        "confirmed_password": "securepassword123!",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "email" in response.data


@pytest.mark.django_db
def test_user_registration_duplicate_email(api_client, user):
    url = reverse("register")
    data = {
        "username": "neuername",
        "email": user.email,
        "password": "securepassword123!",
        "confirmed_password": "securepassword123!",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "email" in response.data
    assert "already exists" in str(response.data["email"])
