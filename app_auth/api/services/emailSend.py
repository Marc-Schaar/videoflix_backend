from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags



def sendActivationMail(user, token,uidb64):
    if settings.DEBUG:
        activation_url = f"https://localhost:5500/{uidb64}/{token}/"

    context = {
        "user": user,
        "activation_url": activation_url,
    }

    html_content = render_to_string("emails/activation.html", context)

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Aktiviere deinen Account",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
