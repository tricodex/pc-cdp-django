"""
URL patterns for wallet app
"""
from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('connect/', views.WalletConnectionView.as_view(), name='connect'),
    path('<str:address>/transactions/',
         views.WalletTransactionListView.as_view(),
         name='transaction-list'),
    path('<str:address>/transactions/<str:transaction_hash>/',
         views.WalletTransactionDetailView.as_view(),
         name='transaction-detail'),
]