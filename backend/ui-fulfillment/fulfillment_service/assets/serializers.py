from rest_framework import serializers

from fulfillment_service.utils import serializers as utils_serializers
from fulfillment_service.wallets.models import Wallet

from .models import Asset, Metrics


class AssetStatisticSerializer(serializers.Serializer):
    long_name = serializers.CharField(
        max_length=50,
        read_only=True,
        label='Detailed name that represents asset on the market, e.g. Apple Inc.',
    )
    current_price = utils_serializers.PositiveBigDecimalField(label='Current price of the asset on the market')
    change_for_day = utils_serializers.PositiveBigDecimalField(
        read_only=True,
        label='Percentage of change in the price of an asset for the current day, '
        'value`s sign is in `profit_direction` field',
    )
    change_for_day_direction = serializers.CharField(
        max_length=10,
        required=False,
        label='Containing `+` or `-`, indicates if the `change_for_day` field positive or negative',
    )
    profit = utils_serializers.PositiveBigDecimalField(
        required=False,
        label='Revenue/loss of the asset from the date of purchase, used only for purchased assets, '
        'value`s sign is in `profit_direction` field',
    )
    profit_direction = serializers.CharField(
        max_length=10,
        required=False,
        label='Containing `+` or `-`, indicates if the `profit` field positive or negative',
    )


class AssetSerializer(serializers.ModelSerializer):
    part_of_portfolio = utils_serializers.PercentageIntegerField(label=Asset.part_of_portfolio.__doc__)
    statistics = AssetStatisticSerializer(required=False)

    class Meta:
        model = Asset
        fields = (
            'part_of_portfolio',
            'overall_sum',
            'asset_name',
            'statistics',
        )
        read_only_fields = ('overall_sum',)


class MetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = (
            'rate_of_return',
            'volatility',
            'value_at_risk',
        )


class AssetWithMetricsSerializer(serializers.Serializer):
    metrics = MetricsSerializer()
    assets = AssetSerializer(many=True)
    invested_sum = utils_serializers.PositiveBigDecimalField(
        label='The sum that is suggested to invest/invested in the assets',
    )

    def create(self, validated_data):
        metrics = Metrics(**validated_data['metrics'])
        invested_sum = validated_data['invested_sum']
        assets = [self.create_asset(asset, invested_sum) for asset in validated_data['assets']]
        return metrics, assets, invested_sum

    @staticmethod
    def create_asset(asset, invested_sum):
        asset_name = asset.get('asset_name')
        part_of_portfolio = asset.get('part_of_portfolio')
        statistics = asset.get('statistics')
        price_per_unit = statistics.get('current_price')
        return Asset(asset_name=asset_name, price_per_unit=price_per_unit).with_part_of_portfolio(
            part_of_portfolio, invested_sum
        )

    def validate_invested_sum(self, invested_sum):
        user = self.context.get('user')
        wallets = Wallet.fits_sum(user, invested_sum)
        if len(wallets) == 0:
            raise serializers.ValidationError('User does not have any wallet with the specified invested sum')
        return invested_sum


class AssetWithMetricsForAdviceSerializer(serializers.Serializer):
    metrics = MetricsSerializer()
    assets = AssetSerializer(many=True)
    suggested_sum = utils_serializers.PositiveBigDecimalField(
        label='The sum that is suggested to invest/invested in the assets',
    )
    risk_level = utils_serializers.PercentageIntegerField(
        read_only=True,
        label='The actual risk level for the investment advice',
    )


class AdviceInputParametersSerializer(serializers.Serializer):
    risk_level = utils_serializers.PercentageIntegerField(
        required=False,
        label='Optional risk level if a user wants to receive an advice with a specific level of risk (from 0 to 100)',
    )
    investing_sum = utils_serializers.PositiveBigDecimalField(
        required=False,
        label='Optional sum that a user is ready to invest. If not provided, max wallets sum is used.',
    )

    def create(self, validated_data):
        investing_sum = validated_data.get(
            'investing_sum', self.validate_investing_sum(self.context.get('default_investing_sum'))
        )
        risk_level = validated_data.get('risk_level', None)
        return investing_sum, risk_level

    def validate_investing_sum(self, investing_sum):
        user = self.context.get('user')
        if investing_sum == 0:
            raise serializers.ValidationError('User does not have any non-empty wallet')
        if len(Wallet.fits_sum(user, investing_sum)) == 0:
            raise serializers.ValidationError('User does not have any wallet with the required investing sum')
        return investing_sum


class AssetDetailedStatisticSerializer(serializers.Serializer):
    previous_close = utils_serializers.PositiveBigDecimalField(
        label='Price at the end of the previous day of the asset on the market',
    )
    current_price = utils_serializers.PositiveBigDecimalField(label='Current price of the asset on the market')
    change_for_day = utils_serializers.BigDecimalField(
        label='Percentage of change in the price of an asset for the current day',
    )
    change_for_day_direction = serializers.CharField(
        max_length=10,
        required=False,
        label='Containing `+` or `-`, indicates if the `change_for_day` field positive or negative',
    )
    change_for_day_sum = utils_serializers.BigDecimalField(
        label='Change in the price of an asset for the current day',
    )
    change_for_day_sum_direction = serializers.CharField(
        max_length=10,
        required=False,
        label='Containing `+` or `-`, indicates if the `change_for_day_sum` field positive or negative',
    )
    long_name = serializers.CharField(
        max_length=50,
        label='Detailed name that represents asset on the market, e.g. Apple Inc.',
    )
    exchange = serializers.CharField(
        max_length=50,
        label='An exchange where traders can buy and sell securities, e.g. NYSEARCA',
    )
    timezone = serializers.CharField(max_length=50, label='Timezone that is used by an exchange, e.g. EDT')
    currency = serializers.CharField(max_length=50, label='Currency used to trade an asset, e.g. USD')
    volume = serializers.CharField(
        max_length=20,
        allow_null=True,
        label='The total number of shares that are actually traded, e.g. 15.3M',
    )
    day_range_low = utils_serializers.PositiveBigDecimalField(
        label='The lowest price of an asset for the current day',
    )
    day_range_high = utils_serializers.PositiveBigDecimalField(
        label='The highest price of an asset for the current day',
    )
    year_range_low = utils_serializers.PositiveBigDecimalField(
        label='The lowest price of an asset for the last year',
    )
    year_range_high = utils_serializers.PositiveBigDecimalField(
        label='The highest price of an asset for the last year',
    )
    timestamp = serializers.IntegerField(
        min_value=0,
        max_value=2147483647,
        label='The timestamp of the provided info about an asset',
    )
    history = serializers.DictField(
        label='The prices of an asset for the last 5 months in format `timestamp: price at day start`, '
        'e.g. {"1609718400000": 133.09, "1609804800000": 128.48, "1609891200000": 127.31}',
    )
