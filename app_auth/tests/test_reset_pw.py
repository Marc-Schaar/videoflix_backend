import pytest
from django.urls import reverse
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status

@pytest.mark.django_db
def test_reset_request_sends_email( api_client, user):
        url = reverse('password_reset')
        response = api_client.post(url, {"email": user.email})

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
        assert "Reset your Password" in mail.outbox[0].subject


@pytest.mark.django_db
def test_reset_request_invalid_email_no_email_sent(api_client):
        url = reverse('password_reset')
        response = api_client.post(url, {"email": "wrong@example.com"})

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

def test_reset_confirm_updates_password(api_client, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        new_pw = "New-Secure-Password-2026"
        response = api_client.post(url, {"password": new_pw})

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password(new_pw)

def test_reset_confirm_invalid_token_fails(api_client, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': "invalid-token"})

        response = api_client.post(url, {"password": "new-password"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

def test_reset_token_usage_once_only(api_client, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        api_client.post(url, {"password": "password123"})

        response = api_client.post(url, {"password": "newpassword456"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
