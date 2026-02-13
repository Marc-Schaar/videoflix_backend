import pytest
from app_auth.api.services.send_mail import send_activation_mail


@pytest.mark.django_db
def test_send_activation_email(user, mailoutbox):
    token = "token123"
    uid = "uid456"

    send_activation_mail(user, token, uid)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert msg.subject == "Confirm your Email"
    assert msg.to == [user.email]
    assert f"{uid}/{token}" in msg.body
    assert len(msg.alternatives) == 1
