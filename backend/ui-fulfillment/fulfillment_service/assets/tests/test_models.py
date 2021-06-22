from decimal import Decimal

import pytest

from fulfillment_service.assets.tests.factories import AssetFactory
from fulfillment_service.wallets.tests.factories import TransactionFactory

pytestmark = pytest.mark.django_db


class TestAsset:
    def test_part_of_portfolio_is_100_for_user_with_one_assets(self):
        asset = AssetFactory()
        assert asset.part_of_portfolio == 100

    def test_part_of_portfolio_is_correct_for_user_with_multiple_assets(self):
        transaction = TransactionFactory()
        asset = AssetFactory(overall_sum=Decimal('100'), transaction=transaction)
        AssetFactory(overall_sum=Decimal('500'), transaction=transaction)
        AssetFactory(overall_sum=Decimal('400'), transaction=transaction)
        AssetFactory()  # create asset for another transaction
        assert asset.part_of_portfolio == 10
