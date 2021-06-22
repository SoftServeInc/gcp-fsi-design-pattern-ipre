import itertools

import more_itertools
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from fulfillment_service.utils.views import date_to_timestamp

from .models import Transaction, Wallet
from .serializers import TransactionSerializer, WalletSerializer, WalletTopUpInputParametersSerializer

DECIMAL_PLACES = settings.DECIMAL_PLACES


class WalletListCreateAPIView(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing wallets for the logged in user.

    post:
    Create a new wallet for the logged in user.
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    def filter_queryset(self, queryset):
        user = self.request.user
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionListAPIView(generics.ListAPIView):
    """
    get:
    Return a list of all the existing transactions for the specified wallet
    """

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def filter_queryset(self, queryset):
        wallet_id = self.kwargs.get('wallet_id')
        return queryset.filter(wallet__id=wallet_id, wallet__user=self.request.user)


class TopUpWalletAPIView(APIView):
    def post(self, request, wallet_id):
        """
        Creates transaction with a positive sum and appropriate transaction name
        """
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=self.request.user)
        except Wallet.DoesNotExist:
            return Response('User does not have specified wallet', status.HTTP_400_BAD_REQUEST)
        serializer = WalletTopUpInputParametersSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        sum = serializer.validated_data.get('sum')
        Transaction.objects.create(
            name='Top-up the wallet',
            sum=sum,
            wallet=wallet,
        )
        return Response('Wallet has been replenished', status.HTTP_201_CREATED)


class ExpensesStatisticsAPIView(APIView):
    def get(self, request):
        """
        Returns statistics by day as a timestamp with `purchases` and `sells` fields.
        For example:
        `{
            "1622678400": {
                "purchases": 8232.49,
                "sells": 5000.0
            },
            "1623024000": {
                "purchases": 600.0,
                "sells": 0
            }
        }`
        """
        transactions_with_sum_and_datetime = (
            Transaction.objects.filter(wallet__user=self.request.user)
            .values_list('created_at', 'sum')
            .order_by('created_at__date')
        )
        transactions_by_dates = itertools.groupby(transactions_with_sum_and_datetime, lambda t: t[0].date())
        dates_by_sums = itertools.starmap(
            lambda date, transactions: (
                date,
                more_itertools.partition(lambda t: t < 0, (sum for (_, sum) in transactions)),
            ),
            transactions_by_dates,
        )
        dates_by_statistics = {
            date_to_timestamp(date): {
                'purchases': round(sum(purchases), DECIMAL_PLACES),
                'sells': round(abs(sum(sells)), DECIMAL_PLACES),
            }
            for date, (purchases, sells) in dates_by_sums
        }

        return Response(dates_by_statistics)
