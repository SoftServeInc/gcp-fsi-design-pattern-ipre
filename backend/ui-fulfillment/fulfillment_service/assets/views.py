import logging

from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from fulfillment_service.assets.exceptions import MLServiceError
from fulfillment_service.assets.models import Asset
from fulfillment_service.utils.views import get_concurrent
from fulfillment_service.wallets.models import NoWalletsForUserError, Wallet

from .helpers import MLServiceProvider, UserPortfolio
from .serializers import (
    AdviceInputParametersSerializer,
    AssetDetailedStatisticSerializer,
    AssetSerializer,
    AssetWithMetricsForAdviceSerializer,
    AssetWithMetricsSerializer,
    MetricsSerializer,
)

logger = logging.getLogger(__name__)


class AssetsWithMetricsAPIView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Contains metrics with list of assets. '
                'If ML service is unavailable, statistics field for each asset will be set to `null`',
                AssetWithMetricsSerializer,
            ),
            status.HTTP_204_NO_CONTENT: openapi.Response('User has not purchased assets'),
        }
    )
    def get(self, request):
        """
        Returns purchased assets, metrics, and overall invested sum.
        If user has not purchased any asset, returns 204 (NO CONTENT) status code
        """
        portfolio = UserPortfolio(self.request.user)
        if not portfolio.user_has_portfolio():
            return Response('User has not purchased assets', status.HTTP_204_NO_CONTENT)

        metrics = portfolio.existing_metrics()
        assets = portfolio.existing_assets()
        invested_sum = portfolio.overall_sum(assets)
        assets_with_statistics = get_concurrent(
            lambda asset: asset.with_statistics_no_fail(MLServiceProvider).with_profit().with_directions(),
            assets,
        )

        response = AssetWithMetricsSerializer(
            {
                'metrics': MetricsSerializer(metrics).data,
                'assets': [AssetSerializer(asset).data for asset in assets_with_statistics],
                'invested_sum': invested_sum,
            }
        )
        return Response(response.data)

    @swagger_auto_schema(
        request_body=AssetWithMetricsSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Indicates that the portfolio has been successfully purchased'),
            status.HTTP_409_CONFLICT: openapi.Response(
                'User does not have required sum in the wallet to purchase the assets'
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Received invalid request'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Failed to get info from ML service'),
        },
    )
    @transaction.atomic
    def post(self, request):
        """
        Sells existing portfolio and purchases specified list of assets.
        Requires a list of assets with metrics.
        """
        metrics, assets, invested_sum = self._parse_body(self.request.data, self.request.user)
        wallet_for_transactions = self._wallet_with_max_balance(invested_sum, self.request.user)
        portfolio = UserPortfolio(self.request.user, wallet_for_transactions)

        if portfolio.user_has_portfolio():
            try:
                portfolio.sell_existing()
            except MLServiceError as e:
                logger.exception('Failed to get profit for assets: {}'.format(e))
                return Response('Failed to get profit for assets', status.HTTP_500_INTERNAL_SERVER_ERROR)

        portfolio.purchase(metrics, assets, invested_sum)
        return Response('Portfolio purchased', status.HTTP_201_CREATED)

    @staticmethod
    def _parse_body(data, user):
        serializer = AssetWithMetricsSerializer(data=data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        metrics, assets, invested_sum = serializer.create(serializer.validated_data)
        return metrics, assets, invested_sum

    @staticmethod
    def _wallet_with_max_balance(invested_sum, user):
        return max(Wallet.fits_sum(user, invested_sum), key=lambda w: w.balance)


class PortfolioAdviceAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'investing_sum',
                openapi.IN_QUERY,
                description='Optional sum that a user is ready to invest. If not provided, max wallets sum is used.',
                required=False,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'risk_level',
                openapi.IN_QUERY,
                description='Optional risk level if a user wants to receive an advice with a specific level of risk '
                '(from 0 to 100)',
                required=False,
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Contains metrics with suggested list of assets',
                AssetWithMetricsForAdviceSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                'Got invalid risk level query parameter or user does not have specified sum'
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Failed to get info from ML service'),
        },
    )
    def get(self, request):
        """
        Requests ML services for the portfolio advice, uses wallet with max balance as an investing sum,
        and requests additional info about every recommendation asset.
        Optionally, accepts the risk level and investing_sum.
        Returns a list of assets, metrics, suggested investing sum, and actual risk level.
        """

        investing_sum, risk_level = self._parse_query_params(self.request.user, self.request.query_params)
        try:
            assets, metrics, risk_level = MLServiceProvider.get_advice(
                self.request.user.ml_uuid, investing_sum, risk_level
            )
        except MLServiceError as e:
            logger.exception('Failed to get advice from the service: {}'.format(str(e)))
            return Response('Failed to get advice from the service', status.HTTP_500_INTERNAL_SERVER_ERROR)

        assets_with_statistics = get_concurrent(
            lambda asset: asset.with_statistics_no_fail(MLServiceProvider).with_directions(),
            assets,
        )

        response = AssetWithMetricsForAdviceSerializer(
            {
                'metrics': MetricsSerializer(metrics).data,
                'assets': [AssetSerializer(asset).data for asset in assets_with_statistics],
                'suggested_sum': investing_sum,
                'risk_level': risk_level,
            }
        )
        return Response(response.data)

    def _parse_query_params(self, user, query_params):
        context = {
            'user': user,
            'default_investing_sum': self._default_investing_sum(user),
        }
        serializer = AdviceInputParametersSerializer(data=query_params, context=context)
        serializer.is_valid(raise_exception=True)
        investing_sum, risk_level = serializer.create(serializer.validated_data)
        return investing_sum, risk_level

    @staticmethod
    def _default_investing_sum(user):
        try:
            return Wallet.max_balance(user)
        except NoWalletsForUserError:
            raise serializers.ValidationError('User does not have any wallet')


class AssetDetailedStatisticAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'asset_name',
                openapi.IN_PATH,
                description='The short name of an asset that represents it on a market, e.g. GOOG',
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Contains detailed info about the specified asset',
                AssetDetailedStatisticSerializer,
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('Specified asset does not exist'),
        },
    )
    def get(self, request, asset_name):
        """
        Provides detailed info about asset:
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
        - forward_dividend;
        - dividend_yield;
        - timestamp;
        - history (for last 5 months).
        """
        asset = Asset(asset_name=asset_name).with_detailed_statistics(MLServiceProvider).with_directions()
        return Response(AssetDetailedStatisticSerializer(asset.statistics).data)
