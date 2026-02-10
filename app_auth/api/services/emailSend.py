from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage




def sendActivationMail(user, token,uidb64):
    if settings.DEBUG:
        activation_url = f"https://localhost:5500/{uidb64}/{token}/"
    else:
        activation_url = f"https://domain.de/activate/{uidb64}/{token}/"

    context = {
        "user": user,
        "activation_url": activation_url,
    }

    logo_path = finders.find('images/logo.svg')

    html_content = render_to_string("emails/activation.html", context)

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Confirm your Email",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    with open(logo_path, 'rb') as f:
        logo_data = f.read()

    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo_id>')  
    msg.attach(logo)

    msg.send()
