from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings

from urllib.parse import urlencode


def send_invite(user):
    link = f"{settings.UI_DOMAIN}/login"

    html_message = render_to_string('email_templates/invite.html', {'link': link})
    plain_message = strip_tags(html_message)

    send_mail(
        "Sacred Garden: You've been invited",
        plain_message,
        settings.PASSWORD_INVITE_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )


def send_reset_password(user):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)

    query = urlencode({'userId': user.id, 'resetPasswordToken': token})
    link = f"{settings.UI_DOMAIN}/login?{query}"

    html_message = render_to_string('email_templates/password_reset.html', {'link': link})
    plain_message = strip_tags(html_message)

    send_mail(
        "Sacred Garden: Account password reset",
        plain_message,
        settings.PASSWORD_RESET_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )
