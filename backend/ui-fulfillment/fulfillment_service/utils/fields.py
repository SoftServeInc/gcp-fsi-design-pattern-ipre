from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

DECIMAL_PLACES = settings.DECIMAL_PLACES


class BigDecimalField(models.DecimalField):
    description = 'Decimal field with max 15 unit digits and {} decimal places'.format(DECIMAL_PLACES)

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 15 + DECIMAL_PLACES
        kwargs['decimal_places'] = DECIMAL_PLACES
        super().__init__(*args, **kwargs)


class PositiveBigDecimalField(BigDecimalField):
    description = 'Positive big decimal field'

    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [MinValueValidator(Decimal('0.01'))]
        super().__init__(*args, **kwargs)
