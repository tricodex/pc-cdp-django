"""
URL patterns for API management
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('keys/', views.APIKeyListView.as_view(), name='api-key-list'),
    path('keys/<int:pk>/', views.APIKeyDetailView.as_view(), name='api-key-detail'),
    path('keys/<int:pk>/usage/', views.APIKeyUsageView.as_view(), name='api-key-usage'),
]