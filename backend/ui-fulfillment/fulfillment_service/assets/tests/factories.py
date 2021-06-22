from django.conf import settings
from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal

from fulfillment_service.assets.models import Asset, Metrics
from fulfillment_service.users.tests.factories import UserFactory
from fulfillment_service.wallets.tests.factories import TransactionFactory

DECIMAL_PLACES = settings.DECIMAL_PLACES


class AssetFactory(DjangoModelFactory):
    price_per_unit = FuzzyDecimal(0.01, 100.0, precision=DECIMAL_PLACES)
    overall_sum = LazyAttribute(lambda a: a.price_per_unit * FuzzyDecimal(0.0, 20.0, precision=DECIMAL_PLACES).fuzz())
    asset_name = Faker('cryptocurrency_code')
    transaction = SubFactory(TransactionFactory)

    class Meta:
        model = Asset


class MetricsFactory(DjangoModelFactory):
    rate_of_return = FuzzyDecimal(0.01, 100.0, precision=DECIMAL_PLACES)
    volatility = FuzzyDecimal(0.01, 100.0, precision=DECIMAL_PLACES)
    value_at_risk = FuzzyDecimal(0.01, 100.0, precision=DECIMAL_PLACES)
    user = SubFactory(UserFactory)

    class Meta:
        model = Metrics
