import pytest
from django.conf import settings
from app_auth.api.services.send_mail import send_activation_mail, send_password_reset_mail


@pytest.mark.django_db
def test_send_activation_email(user, mailoutbox):
    settings.RQ_QUEUES['default']['ASYNC'] = False

    token = "token123"
    uid = "uid456"

    send_activation_mail(user.id, token, uid)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert msg.subject == "Confirm your Email"
    assert msg.to == [user.email]

    assert uid in msg.body
    assert token in msg.body
    assert settings.FRONTEND_DOMAIN in msg.body

    assert len(msg.alternatives) == 1
    assert msg.alternatives[0][1] == "text/html"


@pytest.mark.django_db
def test_send_password_reset_email(user, mailoutbox):
    settings.RQ_QUEUES['default']['ASYNC'] = False

    token = "reset-token-789"
    uid = "reset-uid-abc"

    send_password_reset_mail(user.id, token, uid)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]

    assert msg.subject == "Reset your Password"

    assert msg.to == [user.email]

    assert uid in msg.body
    assert token in msg.body
    assert settings.FRONTEND_DOMAIN in msg.body

    assert len(msg.alternatives) == 1
    assert msg.alternatives[0][1] == "text/html"
    html_content = msg.alternatives[0][0]
    assert uid in html_content
    assert token in html_content
