from decimal import Decimal

import pytest

from fulfillment_service.users.tests.factories import UserFactory
from fulfillment_service.wallets.models import NoWalletsForUserError, Wallet

from .factories import TransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db


class TestWalletModel:
    def test_balance_is_zero_for_wallet_without_transactions(self):
        wallet = WalletFactory()
        assert wallet.balance == 0

    def test_max_balance_raises_exception_for_user_without_wallets(self):
        user = UserFactory()
        with pytest.raises(NoWalletsForUserError):
            Wallet.max_balance(user)

    def test_max_balance_is_correct_for_user_with_one_wallet(self):
        wallet = WalletFactory()
        TransactionFactory(sum=Decimal('100'), wallet=wallet)
        assert Wallet.max_balance(wallet.user) == Decimal('100')

    def test_max_balance_is_correct_for_user_with_multiple_wallets(self):
        user = UserFactory()
        wallet1, wallet2 = WalletFactory.create_batch(2, user=user)
        TransactionFactory(sum=Decimal('100'), wallet=wallet1)
        TransactionFactory(sum=Decimal('90'), wallet=wallet2)
        assert Wallet.max_balance(user) == Decimal('100')

    def test_for_balance_wallet_takes_only_transactions_for_the_specified_wallet(self):
        wallet = WalletFactory()
        TransactionFactory(sum=Decimal('50.45'), wallet=wallet)
        TransactionFactory(sum=Decimal('40'), wallet=wallet)
        TransactionFactory(sum=Decimal('-20.16'), wallet=wallet)
        TransactionFactory()  # create transaction in another wallet

        assert wallet.balance == Decimal('70.29')
