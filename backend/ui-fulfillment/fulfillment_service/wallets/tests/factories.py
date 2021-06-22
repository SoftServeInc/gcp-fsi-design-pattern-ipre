from django.conf import settings
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal

from fulfillment_service.users.tests.factories import UserFactory
from fulfillment_service.wallets.models import Transaction, Wallet

DECIMAL_PLACES = settings.DECIMAL_PLACES


class WalletFactory(DjangoModelFactory):
    bank_name = Faker('name')
    card_number = Faker('credit_card_number')
    user = SubFactory(UserFactory)

    class Meta:
        model = Wallet


class TransactionFactory(DjangoModelFactory):
    sum = FuzzyDecimal(0.0, 1000.0, precision=DECIMAL_PLACES)
    name = Faker('name')
    wallet = SubFactory(WalletFactory)

    class Meta:
        model = Transaction
