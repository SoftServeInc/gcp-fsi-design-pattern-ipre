import uuid
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from fulfillment_service.users.tests.factories import UserFactory
from fulfillment_service.utils.tests import lists_equal
from fulfillment_service.wallets.models import Transaction, Wallet
from fulfillment_service.wallets.views import TopUpWalletAPIView, TransactionListAPIView, WalletListCreateAPIView

from .factories import TransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestWalletListCreateAPIView:
    def setup_method(self):
        self.url = '/wallets/'
        self.factory = APIRequestFactory()
        self.view = WalletListCreateAPIView.as_view()
        self.user = UserFactory()
        self.users_wallet = WalletFactory(user=self.user)
        WalletFactory()  # create wallet for another user

    def test_wallet_list_returns_only_users_wallets(self):
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == str(self.users_wallet.id)

    def test_wallet_list_returns_correct_wallet_data(self):
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        assert response.status_code == 200
        assert response.data[0]['bank_name'] == self.users_wallet.bank_name
        assert response.data[0]['card_number'] == self.users_wallet.card_number
        assert response.data[0]['balance'] == 0

    def test_wallet_list_fails_for_unauthenticated_user(self):
        request = self.factory.get(self.url)

        response = self.view(request)
        assert response.status_code == 403

    def test_wallet_post_correctly_adds_wallet_to_the_logged_in_user(self):
        request = self.factory.post(self.url, {'bank_name': 'bank name #3', 'card_number': '1234567812345678'})
        force_authenticate(request, user=self.user)

        response = self.view(request)
        expected_wallet = Wallet.objects.filter(user=self.user).exclude(id=self.users_wallet.id)[0]
        assert response.status_code == 201
        assert response.data == {
            'id': str(expected_wallet.id),
            'bank_name': expected_wallet.bank_name,
            'card_number': expected_wallet.card_number,
            'balance': 0,
        }

    def test_wallet_post_fails_for_unauthenticated_user(self):
        request = self.factory.post(self.url, {'bank_name': 'bank name #3', 'card_number': '1234567812345678'})

        response = self.view(request)
        assert response.status_code == 403


class TestTransactionListAPIView:
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.view = TransactionListAPIView.as_view()
        self.user = UserFactory()
        self.wallet = WalletFactory(user=self.user)
        self.url = '/wallets/{}/transactions/'.format(self.wallet.id)
        TransactionFactory()  # create transaction in another wallet

    def test_transaction_get_does_not_return_transactions_for_stranger_wallet(self):
        stranger_wallet = WalletFactory()
        TransactionFactory(sum=Decimal('10.1'), wallet=stranger_wallet)
        TransactionFactory(sum=Decimal('-100.99'), wallet=stranger_wallet)
        TransactionFactory(sum=Decimal('48'), wallet=stranger_wallet)
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=stranger_wallet.id)
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_transaction_get_returns_only_transactions_of_specified_wallet(self):
        TransactionFactory(sum=Decimal('10.1'), wallet=self.wallet)
        TransactionFactory(sum=Decimal('-100.99'), wallet=self.wallet)
        TransactionFactory(sum=Decimal('48'), wallet=self.wallet)
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=self.wallet.id)
        assert response.status_code == 200
        assert len(response.data) == 3
        actual_response = [t['sum'] for t in response.data]
        expected_response = [Decimal('10.1'), Decimal('100.99'), Decimal('48')]
        assert lists_equal(actual_response, expected_response)

    def test_transaction_get_returns_transactions_with_correct_directions_and_sums(self):
        TransactionFactory(sum=Decimal('10.1'), wallet=self.wallet)
        TransactionFactory(sum=Decimal('-100.99'), wallet=self.wallet)
        TransactionFactory(sum=Decimal('48'), wallet=self.wallet)
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=self.wallet.id)
        assert response.status_code == 200
        assert len(response.data) == 3
        actual_response = [{'sum_direction': t['sum_direction'], 'sum': t['sum']} for t in response.data]
        expected_response = [
            {'sum_direction': '+', 'sum': Decimal('10.1')},
            {'sum_direction': '-', 'sum': Decimal('100.99')},
            {'sum_direction': '+', 'sum': Decimal('48')},
        ]
        assert lists_equal(actual_response, expected_response, sort_by=lambda t: t['sum'])

    def test_transaction_get_fails_for_unauthorized_user(self):
        request = self.factory.get(self.url)

        response = self.view(request, wallet_id=self.wallet.id)
        assert response.status_code == 403


class TestTopUpWalletAPIView:
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.view = TopUpWalletAPIView.as_view()
        self.user = UserFactory()
        self.wallet = WalletFactory(user=self.user)
        self.url = '/wallets/{}/topup/'.format(self.wallet.id)
        TransactionFactory()  # create transaction in another wallet

    def test_topup_with_invalid_uuid_returns_bad_request_status(self):
        request = self.factory.post(self.url, {'sum': '1'})
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=uuid.uuid4())
        assert response.status_code == 400

    @pytest.mark.parametrize('topup_sum', ['-1', '0', '1.123'])
    def test_topup_with_invalid_sum_returns_bad_request_status(self, topup_sum):
        request = self.factory.post(self.url, {'sum': topup_sum})
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=self.wallet.id)
        assert response.status_code == 400

    def test_topup_with_stranger_wallet_returns_bad_request_status(self):
        stranger_wallet = WalletFactory()
        request = self.factory.post('/wallets/{}/topup/'.format(stranger_wallet.id), {'sum': '123.45'})
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=stranger_wallet.id)
        assert response.status_code == 400

    def test_topup_creates_transaction_with_valid_sum(self):
        request = self.factory.post(self.url, {'sum': '123.45'})
        force_authenticate(request, user=self.user)

        response = self.view(request, wallet_id=self.wallet.id)
        assert response.status_code == 201
        transactions = Transaction.objects.filter(wallet=self.wallet.id)
        assert len(transactions) == 1
        assert transactions[0].sum == Decimal('123.45')
        assert transactions[0].name == 'Top-up the wallet'
