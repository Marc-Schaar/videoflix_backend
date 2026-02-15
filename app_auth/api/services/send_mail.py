from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage


def send_activation_mail(user, token, uidb64):
    activation_url = f"{settings.FRONTEND_DOMAIN}/{uidb64}/{token}/"

    context = {
        "user": user,
        "activation_url": activation_url,
    }

    logo_path = finders.find("images/logo.svg")

    html_content = render_to_string("account_activation_email.html", context)

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Confirm your Email",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    if logo_path:
        with open(logo_path, "rb") as f:
            logo_data = f.read()
        logo = MIMEImage(logo_data)
        logo.add_header("Content-ID", "<logo_id>")
        msg.attach(logo)

    msg.send()


def send_password_reset_mail(user, token, uidb64):
    password_reset_url = f"{settings.FRONTEND_DOMAIN}/{uidb64}/{token}/"
    logo_path = finders.find("images/logo.svg")

    context = {
        "user": user,
        "password_reset_url": password_reset_url,
    }

    html_content = render_to_string("reset_password_email.html", context)

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Passwort zurücksetzen",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    if logo_path:
        with open(logo_path, "rb") as f:
            logo_data = f.read()
        logo = MIMEImage(logo_data)
        logo.add_header("Content-ID", "<logo_id>")
        msg.attach(logo)

    msg.send()
