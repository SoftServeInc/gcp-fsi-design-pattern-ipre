from decimal import Decimal

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from fulfillment_service.assets.exceptions import MLServiceError
from fulfillment_service.assets.helpers import BasicStatistic, DetailedStatistics
from fulfillment_service.assets.models import Asset, Metrics
from fulfillment_service.assets.tests.factories import AssetFactory, MetricsFactory
from fulfillment_service.assets.views import (
    AssetDetailedStatisticAPIView,
    AssetsWithMetricsAPIView,
    PortfolioAdviceAPIView,
)
from fulfillment_service.users.tests.factories import UserFactory
from fulfillment_service.utils.tests import lists_equal
from fulfillment_service.wallets.models import Transaction
from fulfillment_service.wallets.tests.factories import TransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db

HELPERS_CLASS_PATH = 'fulfillment_service.assets.helpers.MLServiceProvider'


class TestAssetsWithMetricsAPIView:
    def setup_method(self):
        self.url = '/assets/'
        self.factory = APIRequestFactory()
        self.view = AssetsWithMetricsAPIView.as_view()
        self.user = UserFactory()

        AssetFactory()  # create asset for another user
        MetricsFactory()  # create metrics for another user

    @staticmethod
    def patch(mocker):
        def set_profit_stub(_self, asset):
            if asset.asset_name == 'ABC':
                setattr(_self, 'profit', Decimal('500'))
            elif asset.asset_name == 'BCD':
                setattr(_self, 'profit', Decimal('-40'))
            else:
                setattr(_self, 'profit', Decimal('0'))

        def get_basic_statistics_by_asset_stub(asset_name):
            return BasicStatistic(
                long_name='ABC Inc.',
                current_price=Decimal('84.10'),
                change_for_day=Decimal('35.12') if asset_name == 'OGGO' else Decimal('-2.73'),
            )

        mocker.patch(
            '{}.get_basic_statistics_by_asset'.format(HELPERS_CLASS_PATH),
            new=get_basic_statistics_by_asset_stub,
        )
        mocker.patch('fulfillment_service.assets.helpers.BasicStatistic.set_profit', new=set_profit_stub)

    @staticmethod
    def patch_error(mocker):
        mocker.patch(
            '{}.get_basic_statistics_by_asset'.format(HELPERS_CLASS_PATH),
            side_effect=MLServiceError('Some exception..'),
        )


class TestGetAssetsWithMetricsAPIView(TestAssetsWithMetricsAPIView):
    def setup_method(self):
        super().setup_method()
        self.wallet = WalletFactory(user=self.user)
        self.request = self.factory.get(self.url)
        force_authenticate(self.request, user=self.user)

    def test_view_fails_if_another_user_has_assets(self):
        response = self.view(self.request)
        assert response.status_code == 204

    def test_invested_sum_equals_to_assets_of_user(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.45'), wallet=self.wallet)
        AssetFactory(overall_sum=Decimal('100.40'), transaction=transaction)
        AssetFactory(overall_sum=Decimal('550.90'), transaction=transaction)
        AssetFactory(overall_sum=Decimal('349.15'), transaction=transaction)
        MetricsFactory(user=self.user)

        response = self.view(self.request)
        assert response.status_code == 200
        assert response.data['invested_sum'] == '1000.45'

    def test_view_responses_user_metrics(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.45'), wallet=self.wallet)
        AssetFactory(overall_sum=Decimal('100.40'), transaction=transaction)
        AssetFactory(overall_sum=Decimal('550.90'), transaction=transaction)
        AssetFactory(overall_sum=Decimal('349.15'), transaction=transaction)
        MetricsFactory(
            rate_of_return=Decimal('98.76'), volatility=Decimal('5'), value_at_risk=Decimal('0.9'), user=self.user
        )

        response = self.view(self.request)
        assert response.status_code == 200
        metrics = response.data['metrics']
        assert metrics['rate_of_return'] == '98.76'
        assert metrics['volatility'] == '5.00'
        assert metrics['value_at_risk'] == '0.90'

    def test_view_responses_assets_with_all_required_fields(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.45'), wallet=self.wallet)
        AssetFactory(asset_name='ABC', overall_sum=Decimal('1000.45'), transaction=transaction)
        MetricsFactory(user=self.user)

        response = self.view(self.request)
        assert response.status_code == 200
        assets = response.data['assets']
        assert len(assets) == 1
        assert assets[0]['part_of_portfolio'] == 100
        assert assets[0]['overall_sum'] == '1000.45'
        assert assets[0]['asset_name'] == 'ABC'

    def test_view_responses_with_correct_part_of_portfolio_for_multiple_assets(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000'), wallet=self.wallet)
        AssetFactory(asset_name='ABC', overall_sum=Decimal('340'), transaction=transaction)
        AssetFactory(asset_name='BCD', overall_sum=Decimal('660'), transaction=transaction)
        MetricsFactory(user=self.user)

        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['part_of_portfolio'] for asset in response.data['assets']}
        assert len(assets) == 2
        assert assets['ABC'] == 34
        assert assets['BCD'] == 66

    def test_view_responses_with_statistics_from_ml_provider_call(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.41'), wallet=self.wallet)
        AssetFactory(asset_name='OGGO', overall_sum=Decimal('100.41'), transaction=transaction)
        MetricsFactory(user=self.user)

        response = self.view(self.request)
        assert response.status_code == 200
        assets = response.data['assets']
        assert len(assets) == 1
        assert assets[0]['statistics']['long_name'] == 'ABC Inc.'
        assert assets[0]['statistics']['current_price'] == '84.10'
        assert assets[0]['statistics']['change_for_day'] == '35.12'
        assert assets[0]['statistics']['profit'] == '0.00'

    def test_view_responses_with_correct_profit_and_profit_direction(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.41'), wallet=self.wallet)
        AssetFactory(asset_name='ABC', overall_sum=Decimal('100.41'), transaction=transaction)
        AssetFactory(asset_name='BCD', overall_sum=Decimal('100.41'), transaction=transaction)
        MetricsFactory(user=self.user)

        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['statistics'] for asset in response.data['assets']}
        assert len(assets) == 2
        assert assets['ABC']['profit'] == '500.00'
        assert assets['ABC']['profit_direction'] == '+'
        assert assets['BCD']['profit'] == '40.00'
        assert assets['BCD']['profit_direction'] == '-'

    def test_view_responses_with_correct_change_for_day_and_change_for_day_direction(self, mocker):
        self.patch(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.41'), wallet=self.wallet)
        AssetFactory(asset_name='OGGO', overall_sum=Decimal('100.41'), transaction=transaction)
        AssetFactory(asset_name='ABC', overall_sum=Decimal('100.42'), transaction=transaction)
        MetricsFactory(user=self.user)

        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['statistics'] for asset in response.data['assets']}
        assert len(assets) == 2
        assert assets['OGGO']['change_for_day'] == '35.12'
        assert assets['OGGO']['change_for_day_direction'] == '+'
        assert assets['ABC']['change_for_day'] == '2.73'
        assert assets['ABC']['change_for_day_direction'] == '-'

    def test_view_responses_data_without_statistics_if_ml_provider_fails(self, mocker):
        self.patch_error(mocker)
        transaction = TransactionFactory(sum=Decimal('1000.41'), wallet=self.wallet)
        AssetFactory(asset_name='OGGO', overall_sum=Decimal('100.41'), transaction=transaction)
        MetricsFactory(user=self.user)
        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['statistics'] for asset in response.data['assets']}
        assert len(assets) == 1
        assert assets['OGGO'] is None


class TestPostAssetsWithMetricsAPIView(TestAssetsWithMetricsAPIView):
    def setup_method(self):
        super().setup_method()
        self.correct_request_body_with_multiple_assets = {
            'metrics': {
                'rate_of_return': Decimal('1.23'),
                'volatility': Decimal('4.56'),
                'value_at_risk': Decimal('7.8'),
            },
            'assets': [
                {
                    'part_of_portfolio': Decimal('30'),
                    'asset_name': 'NAAAAQ',
                    'statistics': {
                        'current_price': Decimal('43.99'),
                    },
                },
                {
                    'part_of_portfolio': Decimal('70'),
                    'asset_name': 'OGGO',
                    'statistics': {
                        'current_price': Decimal('87.5'),
                    },
                },
            ],
            'invested_sum': Decimal('500'),
        }

    def post_request(self):
        request = self.factory.post(self.url, self.correct_request_body_with_multiple_assets, format='json')
        force_authenticate(request, user=self.user)

        return self.view(request)

    def test_view_fails_if_required_fields_not_passed(self):
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.10'), wallet=wallet)
        del self.correct_request_body_with_multiple_assets['metrics']['volatility']
        del self.correct_request_body_with_multiple_assets['assets'][0]['statistics']

        response = self.post_request()
        assert response.status_code == 400

    def test_view_fails_if_one_wallet_does_not_have_invested_sum(self):
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10.20'), wallet=wallet)

        response = self.post_request()
        assert response.status_code == 400

    def test_view_fails_if_multiple_wallets_do_not_have_invested_sum(self):
        wallet1, wallet2 = WalletFactory.create_batch(2, user=self.user)
        TransactionFactory(sum=Decimal('200.20'), wallet=wallet1)
        TransactionFactory(sum=Decimal('400.99'), wallet=wallet2)

        response = self.post_request()
        assert response.status_code == 400

    def test_view_uses_wallet_which_fits_invested_sum_if_user_has_one_wallet(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('1000.99'), wallet=wallet)

        response = self.post_request()
        assert response.status_code == 201
        assert wallet.balance == Decimal('500.99')

    def test_view_uses_wallet_which_fits_invested_sum_if_user_has_multiple_wallets(self, mocker):
        self.patch(mocker)
        wallet1, wallet2 = WalletFactory.create_batch(2, user=self.user)
        TransactionFactory(sum=Decimal('400.99'), wallet=wallet1)
        TransactionFactory(sum=Decimal('1000.99'), wallet=wallet2)

        response = self.post_request()
        assert response.status_code == 201
        assert wallet1.balance == Decimal('400.99')
        assert wallet2.balance == Decimal('500.99')

    def test_view_uses_wallet_with_max_balance_if_user_has_multiple_wallets_which_fits_invested_sum(self, mocker):
        self.patch(mocker)
        wallet1, wallet2 = WalletFactory.create_batch(2, user=self.user)
        TransactionFactory(sum=Decimal('1500.99'), wallet=wallet1)
        TransactionFactory(sum=Decimal('1000.99'), wallet=wallet2)

        response = self.post_request()
        assert response.status_code == 201
        assert wallet1.balance == Decimal('1000.99')
        assert wallet2.balance == Decimal('1000.99')

    def test_view_correctly_calculates_overall_sum_for_each_asset(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('1000'), wallet=wallet)

        response = self.post_request()
        assert response.status_code == 201
        assets = {asset.asset_name: asset for asset in Asset.objects.filter(transaction__wallet=wallet)}
        assert len(assets) == 2
        assert assets['NAAAAQ'].overall_sum == Decimal('150')
        assert assets['OGGO'].overall_sum == Decimal('350')

    def test_view_does_not_uses_overall_sum_from_request(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('1000'), wallet=wallet)
        self.correct_request_body_with_multiple_assets['assets'][0]['overall_sum'] = Decimal('428.13')
        self.correct_request_body_with_multiple_assets['assets'][1]['overall_sum'] = Decimal('13.53')

        response = self.post_request()
        assert response.status_code == 201
        assets = {asset.asset_name: asset for asset in Asset.objects.filter(transaction__wallet=wallet)}
        assert len(assets) == 2
        assert assets['NAAAAQ'].overall_sum == Decimal('150')
        assert assets['OGGO'].overall_sum == Decimal('350')

    def test_view_correctly_saves_metrics_if_assets_were_not_purchased(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('1000'), wallet=wallet)

        response = self.post_request()
        assert response.status_code == 201
        metrics = Metrics.objects.filter(user=self.user)
        assert len(metrics) == 1
        assert metrics[0].rate_of_return == Decimal('1.23')
        assert metrics[0].volatility == Decimal('4.56')
        assert metrics[0].value_at_risk == Decimal('7.8')

    def test_view_correctly_saves_assets_if_assets_were_not_purchased(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('1000'), wallet=wallet)

        response = self.post_request()
        assert response.status_code == 201
        assets = {asset.asset_name: asset for asset in Asset.objects.filter(transaction__wallet=wallet)}
        assert len(assets) == 2
        assert 'NAAAAQ' in assets
        assert assets['NAAAAQ'].overall_sum == Decimal('150')
        assert assets['NAAAAQ'].price_per_unit == Decimal('43.99')
        assert 'OGGO' in assets
        assert assets['OGGO'].overall_sum == Decimal('350')
        assert assets['OGGO'].price_per_unit == Decimal('87.50')

    def test_view_creates_transaction_for_selling_if_assets_were_not_purchased(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('1000'), wallet=wallet)

        response = self.post_request()
        assert response.status_code == 201
        transactions = [transaction.sum for transaction in Transaction.objects.filter(wallet=wallet)]
        assert len(transactions) == 2
        assert lists_equal(transactions, [Decimal('1000'), Decimal('-500')])

    def test_view_responses_internal_error_if_ml_provider_fails(self, mocker):
        self.patch_error(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(
            rate_of_return=Decimal('98.76'), volatility=Decimal('5'), value_at_risk=Decimal('0.9'), user=self.user
        )
        response = self.post_request()
        assert response.status_code == 500

    def test_data_does_not_change_if_ml_provider_fails(self, mocker):
        self.patch_error(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(asset_name='ABC', overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(asset_name='BCD', overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(asset_name='CDE', overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(
            rate_of_return=Decimal('98.76'), volatility=Decimal('5'), value_at_risk=Decimal('0.9'), user=self.user
        )
        self.post_request()
        metrics = Metrics.objects.filter(user=self.user)
        assets = [asset.asset_name for asset in Asset.objects.filter(transaction__wallet=wallet)]
        transactions = [transaction.sum for transaction in Transaction.objects.filter(wallet=wallet)]
        assert len(metrics) == 1
        assert metrics[0].rate_of_return == Decimal('98.76')
        assert metrics[0].volatility == Decimal('5')
        assert metrics[0].value_at_risk == Decimal('0.9')
        assert len(assets) == 3
        assert lists_equal(assets, ['ABC', 'BCD', 'CDE'])
        assert len(transactions) == 2
        assert lists_equal(transactions, [Decimal('10000.99'), Decimal('-5000.99')])

    def test_view_correctly_replaces_metrics_if_assets_were_purchased_before(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(
            rate_of_return=Decimal('98.76'), volatility=Decimal('5'), value_at_risk=Decimal('0.9'), user=self.user
        )

        response = self.post_request()
        assert response.status_code == 201
        metrics = Metrics.objects.filter(user=self.user)
        assert len(metrics) == 1
        assert metrics[0].rate_of_return == Decimal('1.23')
        assert metrics[0].volatility == Decimal('4.56')
        assert metrics[0].value_at_risk == Decimal('7.8')

    def test_view_correctly_replaces_assets_if_assets_were_purchased_before(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(user=self.user)

        response = self.post_request()
        assert response.status_code == 201
        assets = {asset.asset_name: asset for asset in Asset.objects.filter(transaction__wallet=wallet)}
        assert len(assets) == 2
        assert 'NAAAAQ' in assets
        assert assets['NAAAAQ'].overall_sum == Decimal('150')
        assert assets['NAAAAQ'].price_per_unit == Decimal('43.99')
        assert 'OGGO' in assets
        assert assets['OGGO'].overall_sum == Decimal('350')
        assert assets['OGGO'].price_per_unit == Decimal('87.50')

    def test_view_creates_transaction_for_buying_and_selling_if_assets_were_purchased_before(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(asset_name='Z', overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(asset_name='X', overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(asset_name='Y', overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(user=self.user)

        response = self.post_request()
        assert response.status_code == 201
        transactions = [transaction.sum for transaction in Transaction.objects.filter(wallet=wallet)]
        assert len(transactions) == 4
        assert lists_equal(
            transactions, [Decimal('10000.99'), Decimal('-5000.99'), Decimal('5000.99'), Decimal('-500')]
        )

    def test_view_creates_correct_names_for_transactions_for_buying_and_selling(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(user=self.user)

        response = self.post_request()
        assert response.status_code == 201
        transactions = {transaction.sum: transaction.name for transaction in Transaction.objects.filter(wallet=wallet)}
        assert len(transactions) == 4
        assert transactions[Decimal('5000.99')] == 'Sale of 3 asset(s)'
        assert transactions[Decimal('-500')] == 'Purchase of 2 asset(s)'

    def test_view_fails_if_user_does_not_have_invested_sum_but_sum_of_assets_is_bigger(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('5050.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-5000.99'), wallet=wallet)
        AssetFactory(overall_sum=Decimal('1000.9'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('3501'), transaction=purchased_transaction)
        AssetFactory(overall_sum=Decimal('499.09'), transaction=purchased_transaction)
        MetricsFactory(user=self.user)

        response = self.post_request()
        assert response.status_code == 400

    def test_view_creates_transaction_for_buying_and_selling_if_price_of_assets_has_changed(self, mocker):
        self.patch(mocker)
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('10000.99'), wallet=wallet)
        purchased_transaction = TransactionFactory(sum=Decimal('-1230'), wallet=wallet)
        AssetFactory(
            price_per_unit=Decimal('100'),
            overall_sum=Decimal('1000'),
            asset_name='ABC',
            transaction=purchased_transaction,
        )
        AssetFactory(
            price_per_unit=Decimal('50'),
            overall_sum=Decimal('200'),
            asset_name='BCD',
            transaction=purchased_transaction,
        )
        AssetFactory(
            price_per_unit=Decimal('20'), overall_sum=Decimal('30'), asset_name='CDE', transaction=purchased_transaction
        )
        MetricsFactory(user=self.user)
        expected_overall_sum = Decimal('1500') + Decimal('160') + Decimal('30')

        response = self.post_request()
        assert response.status_code == 201
        transactions = [transaction.sum for transaction in Transaction.objects.filter(wallet=wallet)]
        assert len(transactions) == 4
        assert lists_equal(transactions, [Decimal('10000.99'), Decimal('-1230'), expected_overall_sum, Decimal('-500')])


class TestPortfolioAdviceAPIView:
    def setup_method(self):
        self.url = '/assets/advice/'
        self.factory = APIRequestFactory()
        self.view = PortfolioAdviceAPIView.as_view()
        self.user = UserFactory()
        self.wallet = WalletFactory(user=self.user)
        self.request = self.factory.get(self.url)
        force_authenticate(self.request, user=self.user)
        TransactionFactory(sum=Decimal('1000'), wallet=self.wallet)
        TransactionFactory()  # create transaction for another user

    @staticmethod
    def patch(mocker):
        def get_advice(_user_id, _investing_sum, risk_level=None):
            if not risk_level:
                risk_level = 1
            return (
                [
                    Asset(asset_name='ABC').with_part_of_portfolio(part_of_portfolio=11, investing_sum=_investing_sum),
                    Asset(asset_name='BCD').with_part_of_portfolio(part_of_portfolio=75, investing_sum=_investing_sum),
                    Asset(asset_name='CDE').with_part_of_portfolio(part_of_portfolio=14, investing_sum=_investing_sum),
                ],
                Metrics(
                    rate_of_return=Decimal('53.11'),
                    volatility=Decimal('12.44'),
                    value_at_risk=Decimal('51.66'),
                ),
                risk_level,
            )

        def get_basic_statistics_by_asset_stub(asset_name):
            if asset_name == 'ABC':
                return BasicStatistic(
                    long_name='ABC Inc.',
                    current_price=Decimal('84.10'),
                    change_for_day=Decimal('35.12'),
                )
            elif asset_name == 'BCD':
                return BasicStatistic(
                    long_name='BCD Inc.',
                    current_price=Decimal('39.99'),
                    change_for_day=Decimal('-2.73'),
                )
            elif asset_name == 'CDE':
                return BasicStatistic(
                    long_name='CDE Inc.',
                    current_price=Decimal('1'),
                    change_for_day=Decimal('100'),
                )
            else:
                return BasicStatistic(
                    long_name='ABC Inc.',
                    current_price=Decimal('84.10'),
                    change_for_day=Decimal('0.3'),
                )

        mocker.patch('{}.get_advice'.format(HELPERS_CLASS_PATH), new=get_advice)
        mocker.patch(
            '{}.get_basic_statistics_by_asset'.format(HELPERS_CLASS_PATH),
            new=get_basic_statistics_by_asset_stub,
        )

    @staticmethod
    def patch_error(mocker):
        mocker.patch('{}.get_advice'.format(HELPERS_CLASS_PATH), side_effect=MLServiceError('Some exception..'))

    def test_view_responses_internal_error_if_ml_provider_fails(self, mocker):
        self.patch_error(mocker)
        response = self.view(self.request)
        assert response.status_code == 500

    def test_view_responses_metrics_from_ml_provider_call(self, mocker):
        self.patch(mocker)
        response = self.view(self.request)
        assert response.status_code == 200
        metrics = response.data['metrics']
        assert metrics['rate_of_return'] == '53.11'
        assert metrics['volatility'] == '12.44'
        assert metrics['value_at_risk'] == '51.66'

    def test_view_responses_assets_from_ml_provider_call(self, mocker):
        self.patch(mocker)
        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['part_of_portfolio'] for asset in response.data['assets']}
        assert len(assets) == 3
        assert 'ABC' in assets
        assert assets['ABC'] == 11
        assert 'BCD' in assets
        assert assets['BCD'] == 75
        assert 'CDE' in assets
        assert assets['CDE'] == 14

    def test_view_responses_risk_from_ml_provider_call_if_risk_level_was_not_provided(self, mocker):
        self.patch(mocker)
        response = self.view(self.request)
        assert response.status_code == 200
        assert response.data['risk_level'] == 1

    def test_view_responses_statistics_from_ml_provider_call(self, mocker):
        self.patch(mocker)
        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['statistics'] for asset in response.data['assets']}
        assert len(assets) == 3
        assert assets['ABC']['long_name'] == 'ABC Inc.'
        assert assets['ABC']['current_price'] == '84.10'

        assert assets['BCD']['long_name'] == 'BCD Inc.'
        assert assets['BCD']['current_price'] == '39.99'

        assert assets['CDE']['long_name'] == 'CDE Inc.'
        assert assets['CDE']['current_price'] == '1.00'

    def test_view_responses_correct_change_for_day_with_direction(self, mocker):
        self.patch(mocker)
        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['statistics'] for asset in response.data['assets']}
        assert len(assets) == 3
        assert assets['ABC']['change_for_day'] == '35.12'
        assert assets['ABC']['change_for_day_direction'] == '+'

        assert assets['BCD']['change_for_day'] == '2.73'
        assert assets['BCD']['change_for_day_direction'] == '-'

        assert assets['CDE']['change_for_day'] == '100.00'
        assert assets['CDE']['change_for_day_direction'] == '+'

    def test_view_responses_assets_with_correct_overall_sum_according_to_max_wallet_sum(self, mocker):
        self.patch(mocker)
        response = self.view(self.request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['overall_sum'] for asset in response.data['assets']}
        assert len(assets) == 3
        assert assets['ABC'] == '110.00'
        assert assets['BCD'] == '750.00'
        assert assets['CDE'] == '140.00'

    def test_view_responses_assets_with_correct_overall_sum_according_to_provided_investing_sum(self, mocker):
        self.patch(mocker)
        request = self.factory.get(self.url, {'investing_sum': '500'})
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 200
        assets = {asset['asset_name']: asset['overall_sum'] for asset in response.data['assets']}
        assert len(assets) == 3
        assert assets['ABC'] == '55.00'
        assert assets['BCD'] == '375.00'
        assert assets['CDE'] == '70.00'

    def test_view_responses_risk_level_which_specified_in_request(self, mocker):
        self.patch(mocker)
        request = self.factory.get(self.url, {'risk_level': '99'})
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 200
        assert response.data['risk_level'] == 99

    @pytest.mark.parametrize('risk_level', ['string', '101', '-1'])
    def test_view_returns_bad_request_if_provided_risk_level_is_invalid(self, risk_level):
        request = self.factory.get(self.url, {'risk_level': risk_level})
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 400


class TestPortfolioAdviceAPIViewInvestingSumValidating:
    def setup_method(self):
        self.url = '/assets/advice/'
        self.factory = APIRequestFactory()
        self.view = PortfolioAdviceAPIView.as_view()
        self.user = UserFactory()
        self.advice = (
            {
                'ABC': Decimal('10.60'),
                'BCD': Decimal('75.35'),
                'CDE': Decimal('14.05'),
            },
            Metrics(
                rate_of_return=Decimal('53.11'),
                volatility=Decimal('12.44'),
                value_at_risk=Decimal('51.66'),
            ),
            45.11,
        )
        self.statistics_by_asset = {
            'long_name': 'ABC Inc.',
            'current_price': Decimal('84'),
            'change_for_day': Decimal('-2.73'),
        }
        TransactionFactory()  # create transaction for another user

    def test_view_fails_if_user_does_not_have_wallets(self):
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 400

    def test_view_fails_if_user_does_not_have_specified_investing_sum(self):
        wallet = WalletFactory(user=self.user)
        TransactionFactory(sum=Decimal('100.99'), wallet=wallet)
        request = self.factory.get(self.url, {'investing_sum': '200'})
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 400

    def test_view_fails_if_user_has_wallets_with_zero_balance(self):
        WalletFactory(user=self.user)
        WalletFactory(user=self.user)
        WalletFactory(user=self.user)
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 400

    def test_view_fails_if_investing_sum_is_zero(self):
        WalletFactory(user=self.user)
        WalletFactory(user=self.user)
        WalletFactory(user=self.user)
        request = self.factory.get(self.url, {'investing_sum': '0'})
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 400


class TestAssetDetailedStatisticAPIView:
    def setup_method(self):

        self.factory = APIRequestFactory()
        self.view = AssetDetailedStatisticAPIView.as_view()
        self.user = UserFactory()
        self.asset_name = 'OGGO'
        self.url = '/assets/{}/stat/'.format(self.asset_name)
        self.response = DetailedStatistics(
            previous_close=Decimal('1'),
            current_price=Decimal('1.12'),
            change_for_day=Decimal('-2.12'),
            change_for_day_sum=Decimal('3.12'),
            long_name='Long name',
            exchange='EXC',
            timezone='EDT',
            currency='USD',
            volume='1.3M',
            day_range_low=Decimal('4.2'),
            day_range_high=Decimal('5'),
            year_range_low=Decimal('6.12'),
            year_range_high=Decimal('7.99'),
            timestamp=2147413647,
            history={2143413647: Decimal('1.31'), 2144413647: Decimal('1.45')},
        )

    def test_view_responses_info_from_ml_provider(self, mocker):
        def statistics_by_asset(asset_name):
            if asset_name == self.asset_name:
                return self.response
            else:
                raise Exception('Unexpected asset name')

        mocker.patch('{}.get_statistics_by_asset'.format(HELPERS_CLASS_PATH), new=statistics_by_asset)
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request, self.asset_name)
        assert response.status_code == 200
        assert response.data == {
            'previous_close': '1.00',
            'current_price': '1.12',
            'change_for_day': '2.12',
            'change_for_day_direction': '-',
            'change_for_day_sum': '3.12',
            'change_for_day_sum_direction': '+',
            'long_name': 'Long name',
            'exchange': 'EXC',
            'timezone': 'EDT',
            'currency': 'USD',
            'volume': '1.3M',
            'day_range_low': '4.20',
            'day_range_high': '5.00',
            'year_range_low': '6.12',
            'year_range_high': '7.99',
            'timestamp': 2147413647,
            'history': {'2143413647': Decimal('1.31'), '2144413647': Decimal('1.45')},
        }
