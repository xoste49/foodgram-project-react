from rest_framework.exceptions import ValidationError


def positive_validator(value):
    if value < 0:
        raise ValidationError(
            'Значение не может быть меньше нуля')
