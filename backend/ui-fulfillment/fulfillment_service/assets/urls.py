from django.urls import path

from .views import AssetDetailedStatisticAPIView, AssetsWithMetricsAPIView, PortfolioAdviceAPIView

urlpatterns = [
    path('assets/', AssetsWithMetricsAPIView.as_view()),
    path('assets/<str:asset_name>/stat/', AssetDetailedStatisticAPIView.as_view()),
    path('assets/advice/', PortfolioAdviceAPIView.as_view()),
]
