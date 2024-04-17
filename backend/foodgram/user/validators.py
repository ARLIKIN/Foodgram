import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    if username in settings.FORBIDDEN_NAMES:
        raise ValidationError(
            f'Имя пользователя "{username}" зарезервировано системой'
        )
    forbidden_chars = re.sub(settings.USERNAME_PATTERN, '', username)
    if forbidden_chars:
        forbidden_chars = ''.join(set(forbidden_chars))
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: "{forbidden_chars}"'
        )
    return username
