import logging
from decimal import Decimal

from django.conf import settings
from django.db import models

from fulfillment_service.assets.exceptions import MLServiceError
from fulfillment_service.utils.fields import BigDecimalField, PositiveBigDecimalField
from fulfillment_service.wallets.models import Transaction

logger = logging.getLogger(__name__)


class Asset(models.Model):
    price_per_unit = PositiveBigDecimalField()
    overall_sum = PositiveBigDecimalField(verbose_name='The purchased sum of the specific asset')
    asset_name = models.CharField(
        max_length=20,
        verbose_name='The short name of an asset that represents it on a market, e.g. GOOG',
    )
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    @property
    def part_of_portfolio(self):
        """
        The percentage of an asset's price relative to the entire portfolio.
        :return: integer value from 0 to 100
        """
        if hasattr(self, '_part_of_portfolio'):
            return self._part_of_portfolio
        assets = Asset.objects.filter(transaction__wallet__user=self.transaction.wallet.user)
        portfolio_sum = sum(a.overall_sum for a in assets)
        return round(self.overall_sum * Decimal('100') / portfolio_sum)

    def with_part_of_portfolio(self, part_of_portfolio, investing_sum):
        self._part_of_portfolio = part_of_portfolio
        self.overall_sum = Decimal(part_of_portfolio) * investing_sum / Decimal('100')
        return self

    def with_profit(self):
        if self.statistics is not None:
            self.statistics.set_profit(self)
        return self

    def with_directions(self):
        if self.statistics is not None:
            self.statistics.set_directions()
        return self

    def with_statistics(self, ml_provider):
        self.statistics = ml_provider.get_basic_statistics_by_asset(self.asset_name)
        return self

    def with_detailed_statistics(self, ml_provider):
        self.statistics = ml_provider.get_statistics_by_asset(self.asset_name)
        return self

    def with_statistics_no_fail(self, ml_provider):
        try:
            return self.with_statistics(ml_provider)
        except MLServiceError as e:
            logger.warning('Failed to get basic info about {} asset: {}'.format(self.asset_name, str(e)))
            self.statistics = None
            return self

    @staticmethod
    def purchase_assets(assets, invested_sum, wallet):
        purchasing_transaction = Transaction.objects.create(
            sum=invested_sum * Decimal('-1'),
            wallet=wallet,
            name='Purchase of {} asset(s)'.format(len(assets)),
        )
        for asset in assets:
            asset.transaction = purchasing_transaction
            asset.save()

    @staticmethod
    def sell_assets(assets, overall_sum_with_profit, wallet):
        Transaction.objects.create(
            sum=overall_sum_with_profit,
            wallet=wallet,
            name='Sale of {} asset(s)'.format(len(assets)),
        )
        assets.delete()

    def __str__(self):
        return '{} {}'.format(self.asset_name, self.overall_sum)


class Metrics(models.Model):
    """
    We temporary need Metrics table which represents a state of the purchased assets,
    because the ML service is not yet able to calculate metrics from the list of assets.
    Therefore, we have to save these metrics during portfolio creation.
    """

    rate_of_return = BigDecimalField()
    volatility = PositiveBigDecimalField()
    value_at_risk = BigDecimalField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @staticmethod
    def create_from_representation(metrics, user):
        Metrics.objects.create(
            rate_of_return=metrics.rate_of_return,
            volatility=metrics.volatility,
            value_at_risk=metrics.value_at_risk,
            user=user,
        )

    def __str__(self):
        return 'RoR {}%, Vol {}%, VaR {}%'.format(
            self.rate_of_return,
            self.volatility,
            self.value_at_risk,
        )
