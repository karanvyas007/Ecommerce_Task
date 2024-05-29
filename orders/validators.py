import re
from django.core.exceptions import ValidationError


def password_validator(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isupper() for char in value):
        raise ValidationError("Password must contain at least one capital letter.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError("Password must contain at least one special character.")