from django.forms import ValidationError

def validate_cash(cash: float):
    if cash < 1000:
        raise ValidationError('Необходимо начать с 1000 тг')
