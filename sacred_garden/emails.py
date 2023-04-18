from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail

from django.conf import settings

from urllib.parse import urlencode


def send_reset_password(user):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)

    query = urlencode({'userId': user.id, 'resetPasswordToken': token})
    link = f"{settings.UI_DOMAIN}/login?{query}"

    send_mail(
        "Sacred Garden: Account password reset",
        f"Click following link to reset your password: <a href='{link}'>Open form</a>",
        settings.PASSWORD_RESET_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
