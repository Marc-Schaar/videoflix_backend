import pytest
from django.core import mail
from app_auth.api.services.send_mail import send_activation_mail



@pytest.mark.django_db
def test_send_activation_email(user):

    send_activation_mail(user, "token123", "uid456")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Confirm your Email"
