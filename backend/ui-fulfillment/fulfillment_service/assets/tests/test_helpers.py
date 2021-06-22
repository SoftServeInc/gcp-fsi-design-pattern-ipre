from decimal import Decimal

import pytest
from django.conf import settings

from fulfillment_service.assets.exceptions import MLServiceError
from fulfillment_service.assets.helpers import BasicStatistic, MLServiceProvider
from fulfillment_service.assets.tests.factories import AssetFactory, TransactionFactory
from fulfillment_service.utils.tests import lists_equal

ML_SERVICE_URL = settings.ML_SERVICE_URL

pytestmark = pytest.mark.django_db


class TestMLServiceProviderGetAdvice:
    def setup_method(self):
        self.user_id = 'user_id'
        self.investing_sum = Decimal('1000')
        self.url = ML_SERVICE_URL
        self.provider = MLServiceProvider()
        self.request = {
            'portfolioComposition': {
                'ABC': {
                    'weight': '0.3',
                    'expectedReturn': '0.13',
                    'expectedVolatility': '0.42',
                },
                'BCD': {
                    'weight': '0.15',
                    'expectedReturn': '0.13',
                    'expectedVolatility': '0.42',
                },
                'CDE': {
                    'weight': '0.02',
                    'expectedReturn': '0.13',
                    'expectedVolatility': '0.42',
                },
                'DEF': {
                    'weight': '0.03',
                    'expectedReturn': '0.13',
                    'expectedVolatility': '0.42',
                },
                'EFG': {
                    'weight': '0.5',
                    'expectedReturn': '0.13',
                    'expectedVolatility': '0.42',
                },
            },
            'portfolioMetrics': {
                'expectedReturn': '33.11',
                'annualVolatility': '44',
                'sharpeRatio': '5.5',
            },
            'riskAversion': '0.44',
        }

    def test_fails_if_http_request_fails(self, requests_mock):
        requests_mock.get(self.url, status_code=400)
        with pytest.raises(MLServiceError):
            self.provider.get_advice(self.user_id, self.investing_sum)

    @pytest.mark.parametrize('field', ['portfolioComposition', 'portfolioMetrics', 'riskAversion'])
    def test_fails_if_required_fields_are_not_in_http_response(self, requests_mock, field):
        requests_mock.get(self.url, json=self.request)
        del self.request[field]
        with pytest.raises(MLServiceError):
            self.provider.get_advice(self.user_id, self.investing_sum)

    def test_fails_if_fields_have_invalid_data(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        self.request['riskAversion'] = 'str'
        with pytest.raises(MLServiceError):
            self.provider.get_advice(self.user_id, self.investing_sum)

    def test_risk_level_is_between_0_and_1_in_http_request_if_provided_not_0(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        self.provider.get_advice(self.user_id, self.investing_sum, risk_level=49)
        query_string = requests_mock.request_history[0].qs
        assert query_string['riskaversion'] == ['0.51']

    def test_risk_level_is_1_in_http_request_if_provided_0(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        self.provider.get_advice(self.user_id, self.investing_sum, risk_level=0)
        query_string = requests_mock.request_history[0].qs
        assert query_string['riskaversion'] == ['1']

    def test_risk_level_is_0_in_http_request_if_provided_100(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        self.provider.get_advice(self.user_id, self.investing_sum, risk_level=100)
        query_string = requests_mock.request_history[0].qs
        assert query_string['riskaversion'] == ['0']

    def test_risk_level_is_not_specified_in_http_request_if_not_provided(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        self.provider.get_advice(self.user_id, self.investing_sum)
        query_string = requests_mock.request_history[0].qs
        assert 'riskaversion' not in query_string

    def test_risk_level_is_correctly_rounded_to_integer(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        _, _, risk_level = self.provider.get_advice(self.user_id, self.investing_sum)
        assert risk_level == 56

    def test_assets_weight_are_between_0_and_100(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        transaction = TransactionFactory()
        assets, _, _ = self.provider.get_advice(self.user_id, self.investing_sum)
        for asset in assets:
            asset.transaction = transaction
        weights = [asset.part_of_portfolio for asset in assets]
        assert lists_equal(weights, [30, 15, 2, 3, 50])

    def test_assets_with_zero_weight_are_not_included_in_response(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        expected_length = len(self.request['portfolioComposition'])
        self.request['portfolioComposition']['NAAAAQ'] = {
            'weight': '0',
            'expectedReturn': '0.13',
            'expectedVolatility': '0.42',
        }
        assets, _, _ = self.provider.get_advice(self.user_id, self.investing_sum)
        assert len(assets) == expected_length

    def test_metrics_are_used_from_http_response(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        _, metrics, _ = self.provider.get_advice(self.user_id, self.investing_sum)
        assert metrics.rate_of_return == Decimal('33.11')
        assert metrics.volatility == Decimal('44')
        assert metrics.value_at_risk == Decimal('5.5')


class TestMLServiceProviderGetBasicStatisticsByAsset:
    def setup_method(self):
        self.asset_name = 'ABC'
        self.url = '{}/stat/?asset_name={}'.format(ML_SERVICE_URL, self.asset_name)
        self.provider = MLServiceProvider()
        self.request = {'change_for_day': 1.391809898486656, 'current_price': 2438.0776, 'long_name': 'ABC Inc.'}

    def test_fails_if_http_request_fails(self, requests_mock):
        requests_mock.get(self.url, status_code=400)
        with pytest.raises(MLServiceError):
            self.provider.get_basic_statistics_by_asset(self.asset_name)

    @pytest.mark.parametrize('field', ['current_price', 'change_for_day', 'long_name'])
    def test_fails_if_required_fields_are_not_in_http_response(self, requests_mock, field):
        requests_mock.get(self.url, json=self.request)
        del self.request[field]
        with pytest.raises(MLServiceError):
            self.provider.get_basic_statistics_by_asset(self.asset_name)

    def test_fails_if_fields_have_invalid_data(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        self.request['current_price'] = 'str'
        with pytest.raises(MLServiceError):
            self.provider.get_basic_statistics_by_asset(self.asset_name)

    def test_uses_data_from_response(self, requests_mock):
        requests_mock.get(self.url, json=self.request)
        response = self.provider.get_basic_statistics_by_asset(self.asset_name)
        assert response.current_price == Decimal('2438.08')
        assert response.change_for_day == Decimal('1.39')
        assert response.long_name == 'ABC Inc.'


class TestMLServiceProviderGetStatisticsByAsset:
    def setup_method(self):
        self.asset_name = 'ABC'
        self.detailed_url = '{}/stat/detailed/?asset_name={}'.format(ML_SERVICE_URL, self.asset_name)
        self.history_url = '{}/stat/history/?asset_name={}'.format(ML_SERVICE_URL, self.asset_name)
        self.provider = MLServiceProvider()
        self.detailed = {
            'previous_close': '1.3388',
            'change_for_day': '1.1394689978954204',
            'change_for_day_sum': '1.4076999999999913',
            'currency': 'USD',
            'current_price': '124.9477',
            'day_range_high': '125.36',
            'day_range_low': '123.85',
            'dividend_yield': '0.70999996',
            'exchange': 'NMS',
            'forward_dividend': '0.88',
            'long_name': 'ABC Inc.',
            'timestamp': '1622819095',
            'timezone': 'EDT',
            'volume': '24452230',
            'year_range_high': '145.09',
            'year_range_low': '80.8075',
        }
        self.history = {
            '1609718400000': '1757.5400390625',
            '1609804800000': '1725.0',
            '1609891200000': '1702.6300048828',
            '1609977600000': '1740.0600585938',
            '1610064000000': '1787.9799804688',
            '1620000000000': '2402.7199707031',
            '1620086400000': '2369.7399902344',
            '1620604800000': '2374.8898925781',
            '1620691200000': '2291.8601074219',
            '1622678400000': '2395.0200195312',
            '1622764800000': '2422.5200195312',
        }

    def test_fails_if_http_request_fails(self, requests_mock):
        requests_mock.get(self.detailed_url, status_code=400)
        requests_mock.get(self.history_url, status_code=400)
        with pytest.raises(MLServiceError):
            self.provider.get_statistics_by_asset(self.asset_name)

    @pytest.mark.parametrize('field', ['current_price', 'day_range_low', 'timestamp'])
    def test_fails_if_required_fields_are_not_in_http_response(self, requests_mock, field):
        requests_mock.get(self.detailed_url, json=self.detailed)
        requests_mock.get(self.history_url, json=self.history)
        del self.detailed[field]
        with pytest.raises(MLServiceError):
            self.provider.get_statistics_by_asset(self.asset_name)

    def test_fails_if_fields_have_invalid_data(self, requests_mock):
        requests_mock.get(self.detailed_url, json=self.detailed)
        requests_mock.get(self.history_url, json=self.history)
        self.detailed['day_range_low'] = 'str'
        with pytest.raises(MLServiceError):
            self.provider.get_statistics_by_asset(self.asset_name)

    def test_fails_if_history_values_have_invalid_data(self, requests_mock):
        requests_mock.get(self.detailed_url, json=self.detailed)
        requests_mock.get(self.history_url, json=self.history)
        self.history['1620691200000'] = 'str'
        with pytest.raises(MLServiceError):
            self.provider.get_statistics_by_asset(self.asset_name)

    def test_volume_correctly_transformed(self, requests_mock):
        requests_mock.get(self.detailed_url, json=self.detailed)
        requests_mock.get(self.history_url, json=self.history)
        response = self.provider.get_statistics_by_asset(self.asset_name)
        assert response.volume == '24M'

    def test_uses_detailed_data_from_response(self, requests_mock):
        requests_mock.get(self.detailed_url, json=self.detailed)
        requests_mock.get(self.history_url, json=self.history)
        response = self.provider.get_statistics_by_asset(self.asset_name)
        assert response.previous_close == Decimal('1.34')
        assert response.change_for_day == Decimal('1.14')
        assert response.change_for_day_sum == Decimal('1.41')
        assert response.currency == 'USD'
        assert response.current_price == Decimal('124.95')
        assert response.day_range_high == Decimal('125.36')
        assert response.day_range_low == Decimal('123.85')
        assert response.exchange == 'NMS'
        assert response.long_name == 'ABC Inc.'
        assert response.timestamp == 1622819095
        assert response.timezone == 'EDT'
        assert response.year_range_high == Decimal('145.09')
        assert response.year_range_low == Decimal('80.81')

    def test_uses_history_data_from_response(self, requests_mock):
        requests_mock.get(self.detailed_url, json=self.detailed)
        requests_mock.get(self.history_url, json=self.history)
        response = self.provider.get_statistics_by_asset(self.asset_name)
        assert response.history == {
            1609718400000: Decimal('1757.54'),
            1609804800000: Decimal('1725'),
            1609891200000: Decimal('1702.63'),
            1609977600000: Decimal('1740.06'),
            1610064000000: Decimal('1787.98'),
            1620000000000: Decimal('2402.72'),
            1620086400000: Decimal('2369.74'),
            1620604800000: Decimal('2374.89'),
            1620691200000: Decimal('2291.86'),
            1622678400000: Decimal('2395.02'),
            1622764800000: Decimal('2422.52'),
        }


class TestMLServiceProviderGetProfit:
    def test_correct_for_negative_profit(self):
        asset = AssetFactory(price_per_unit=Decimal('10'), overall_sum=Decimal('100'))
        statistics = BasicStatistic(current_price=Decimal('5'))
        statistics.set_profit(asset)
        assert statistics.profit == Decimal('-50')

    def test_correct_for_positive_profit(self):
        asset = AssetFactory(price_per_unit=Decimal('10'), overall_sum=Decimal('100'))
        statistics = BasicStatistic(current_price=Decimal('30'))
        statistics.set_profit(asset)
        assert statistics.profit == Decimal('200')

    def test_correct_for_not_changed_price(self):
        asset = AssetFactory(price_per_unit=Decimal('10'), overall_sum=Decimal('100'))
        statistics = BasicStatistic(current_price=Decimal('10'))
        statistics.set_profit(asset)
        assert statistics.profit == Decimal('0')
