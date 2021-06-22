import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from millify import millify
from requests.exceptions import HTTPError

from fulfillment_service.assets.exceptions import MLServiceError
from fulfillment_service.assets.models import Asset, Metrics
from fulfillment_service.utils.serializers import abs_with_direction
from fulfillment_service.utils.views import decimal_from_str, get_concurrent, requests_session

ML_SERVICE_URL = settings.ML_SERVICE_URL
logger = logging.getLogger(__name__)


class Statistics:
    def set_directions(self):
        def run_abs_with_direction(field_name):
            if hasattr(self, field_name) and getattr(self, field_name) is not None:
                value, value_direction = abs_with_direction(getattr(self, field_name))
                setattr(self, field_name, value)
                setattr(self, '{}_direction'.format(field_name), value_direction)

        for field in ['profit', 'change_for_day', 'change_for_day_sum']:
            run_abs_with_direction(field)
        return self


class BasicStatistic(Statistics):
    def __init__(self, current_price, long_name=None, change_for_day=None):
        self.long_name = long_name
        self.current_price = current_price
        self.change_for_day = change_for_day

    def set_profit(self, asset):
        self.profit = asset.overall_sum * (self.current_price / asset.price_per_unit - Decimal('1'))


class DetailedStatistics(Statistics):
    def __init__(
        self,
        previous_close,
        current_price,
        change_for_day,
        change_for_day_sum,
        long_name,
        exchange,
        timezone,
        currency,
        volume,
        day_range_low,
        day_range_high,
        year_range_low,
        year_range_high,
        timestamp,
        history,
    ):
        self.previous_close = previous_close
        self.current_price = current_price
        self.change_for_day = change_for_day
        self.change_for_day_sum = change_for_day_sum
        self.long_name = long_name
        self.exchange = exchange
        self.timezone = timezone
        self.currency = currency
        self.volume = volume
        self.day_range_low = day_range_low
        self.day_range_high = day_range_high
        self.year_range_low = year_range_low
        self.year_range_high = year_range_high
        self.timestamp = timestamp
        self.history = history


class MLServiceProvider:
    @staticmethod
    def get_advice(user_id, investing_sum, risk_level=None):
        """
        Returns a list of assets with metrics according to the user_id and (optionally) risk level
        :param investing_sum: the overall sum that is going to be invested in assets from the advice
        :param user_id: ID of the user for who the advice will be created
        :param risk_level: optional level of risk (value from 0 to 100)
        :return: list of assets, metrics (Rate of Return, Volatility, Value at Risk), and risk_level
        """
        params = {'uuid': user_id}
        if risk_level is not None:
            changed_range = Decimal(risk_level) / Decimal('100') if risk_level > 0 else risk_level
            params['riskAversion'] = Decimal('1') - changed_range
        session = requests_session()
        try:
            with session.get(ML_SERVICE_URL, params=params) as response:
                response.raise_for_status()
                data = response.json()
        except HTTPError as e:
            raise MLServiceError(str(e))

        try:
            composition = data['portfolioComposition']
            metrics = data['portfolioMetrics']
            risk_level = round((Decimal('1') - Decimal(data['riskAversion'])) * Decimal('100'))
            assets = [
                Asset(asset_name=name).with_part_of_portfolio(
                    part_of_portfolio=round(Decimal(info['weight']) * Decimal('100')), investing_sum=investing_sum
                )
                for name, info in composition.items()
                if round(Decimal(info['weight']) * Decimal('100')) != Decimal('0')
            ]
            metrics = Metrics(
                rate_of_return=Decimal(metrics['expectedReturn']),
                volatility=Decimal(metrics['annualVolatility']),
                value_at_risk=Decimal(metrics['sharpeRatio']),
            )
            return assets, metrics, risk_level
        except (InvalidOperation, KeyError):
            raise MLServiceError('Required field in ML response has unexpected format or is not present')

    @staticmethod
    def get_basic_statistics_by_asset(asset_name):
        """
        returns minimum statistics for the specified asset
        :param asset_name: the name of asset for which the revenue/loss will be calculated
        :return:
        - description;
        - current price;
        - change for day.
        """
        params = {'asset_name': asset_name}
        session = requests_session()
        try:
            with session.get(ML_SERVICE_URL + '/stat/', params=params) as response:
                response.raise_for_status()
                data = response.json()
        except HTTPError as e:
            raise MLServiceError(str(e))
        try:
            return BasicStatistic(
                long_name=data['long_name'],
                current_price=decimal_from_str(data['current_price']),
                change_for_day=decimal_from_str(data['change_for_day']),
            )
        except (InvalidOperation, KeyError):
            raise MLServiceError('Required field in ML response has unexpected format or is not present')

    @staticmethod
    def get_statistics_by_asset(asset_name):
        """
        returns statistics for the specified asset
        :param asset_name: the name of asset for which the revenue/loss will be calculated
        :return:
        _ previous close;
        - current_price;
        - change_for_day;
        - change_for_day_sum;
        - long_name;
        - exchange;
        - timezone;
        - currency;
        - volume;
        - day_range_low;
        - day_range_high;
        - year_range_low;
        - year_range_high;
        - timestamp;
        - history (for last 5 months).
        """
        params = {'asset_name': asset_name}
        session = requests_session()
        try:
            with session.get(ML_SERVICE_URL + '/stat/detailed/', params=params) as response:
                response.raise_for_status()
                data = response.json()
            with session.get(ML_SERVICE_URL + '/stat/history/', params=params) as history:
                history.raise_for_status()
                history = history.json()
        except HTTPError as e:
            raise MLServiceError(str(e))

        try:
            history = {int(timestamp): decimal_from_str(price) for timestamp, price in history.items()}
            volume = data.get('volume')
            return DetailedStatistics(
                previous_close=decimal_from_str(data['previous_close']),
                current_price=decimal_from_str(data['current_price']),
                change_for_day=decimal_from_str(data['change_for_day']),
                change_for_day_sum=decimal_from_str(data['change_for_day_sum']),
                long_name=data['long_name'],
                exchange=data['exchange'],
                timezone=data['timezone'],
                currency=data['currency'],
                volume=millify(volume) if volume else None,
                day_range_low=decimal_from_str(data['day_range_low']),
                day_range_high=decimal_from_str(data['day_range_high']),
                year_range_low=decimal_from_str(data['year_range_low']),
                year_range_high=decimal_from_str(data['year_range_high']),
                timestamp=int(data['timestamp']),
                history=history,
            )
        except (InvalidOperation, KeyError):
            raise MLServiceError('Required field in ML response has unexpected format or is not present')


class UserPortfolio:
    def __init__(self, user, wallet=None):
        self.user = user
        self.wallet = wallet

    def user_has_portfolio(self):
        return self.existing_metrics() is not None

    def existing_assets(self):
        return Asset.objects.filter(transaction__wallet__user=self.user)

    def existing_metrics(self):
        return Metrics.objects.filter(user=self.user).first()

    def sell_existing(self):
        assets = self.existing_assets()
        Asset.sell_assets(assets, self.overall_sum_with_profit(assets), self.wallet)
        self.existing_metrics().delete()

    def purchase(self, metrics, assets, invested_sum):
        Metrics.create_from_representation(metrics, self.user)
        Asset.purchase_assets(assets, invested_sum, self.wallet)

    def overall_sum_with_profit(self, assets):
        assets_with_statistics = get_concurrent(
            lambda asset: asset.with_statistics(MLServiceProvider).with_profit(), assets
        )
        return self.overall_sum(assets) + sum(asset.statistics.profit for asset in assets_with_statistics)

    @staticmethod
    def overall_sum(assets):
        return sum(asset.overall_sum for asset in assets)
