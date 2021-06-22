from decimal import Decimal
from enum import Enum

from django.conf import settings
from rest_framework import serializers

DECIMAL_PLACES = settings.DECIMAL_PLACES


class Direction(Enum):
    POSITIVE = '+'
    NEGATIVE = '-'


class BigDecimalField(serializers.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 15 + DECIMAL_PLACES
        kwargs['decimal_places'] = DECIMAL_PLACES
        super().__init__(*args, **kwargs)


class PositiveBigDecimalField(BigDecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['min_value'] = Decimal('0.01')
        super().__init__(*args, **kwargs)


class PercentageIntegerField(serializers.IntegerField):
    def __init__(self, **kwargs):
        kwargs['min_value'] = 0
        kwargs['max_value'] = 100
        super().__init__(**kwargs)


def get_direction(value):
    return Direction.POSITIVE.value if value >= 0 else Direction.NEGATIVE.value


def abs_with_direction(value):
    direction = get_direction(value)
    value = abs(value)
    return value, direction
