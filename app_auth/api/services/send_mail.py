from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_activation_mail(user, token, uidb64):
    activation_url = f"{settings.FRONTEND_DOMAIN}/pages/auth/activate.html?uid={uidb64}&token={token}"


    context = {
        "user": user,
        "activation_url": activation_url,
    }

    html_content = render_to_string("account_activation_email.html", context)

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Confirm your Email",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()


def send_password_reset_mail(user, token, uidb64):
    password_reset_url = f"{settings.FRONTEND_DOMAIN}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
   
    context = {
        "user": user,
        "password_reset_url": password_reset_url,
    }

    html_content = render_to_string("reset_password_email.html", context)

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Reset your Password",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()
