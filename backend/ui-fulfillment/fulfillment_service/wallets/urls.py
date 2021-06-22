from django.urls import path

from .views import ExpensesStatisticsAPIView, TopUpWalletAPIView, TransactionListAPIView, WalletListCreateAPIView

urlpatterns = [
    path('wallets/', WalletListCreateAPIView.as_view()),
    path('wallets/expenses/stat/', ExpensesStatisticsAPIView.as_view()),
    path('wallets/<uuid:wallet_id>/topup/', TopUpWalletAPIView.as_view()),
    path('wallets/<uuid:wallet_id>/transactions/', TransactionListAPIView.as_view()),
]
