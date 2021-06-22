from rest_framework import serializers

from fulfillment_service.utils import serializers as utils_serializers
from fulfillment_service.utils.serializers import get_direction

from .models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = (
            'id',
            'bank_name',
            'card_number',
            'balance',
        )


class TransactionSerializer(serializers.ModelSerializer):
    sum_direction = serializers.SerializerMethodField()
    sum = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'created_at',
            'name',
            'sum',
            'sum_direction',
        )
        read_only_fields = (
            'created_at',
            'name',
            'sum',
            'sum_direction',
        )

    @staticmethod
    def get_sum_direction(transaction):
        return get_direction(transaction.sum)

    @staticmethod
    def get_sum(transaction):
        return abs(transaction.sum)


class WalletTopUpInputParametersSerializer(serializers.Serializer):
    sum = utils_serializers.PositiveBigDecimalField(label='the sum for which user needs to top up the wallet')
