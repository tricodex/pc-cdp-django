"""
URL patterns for agent endpoints
"""
from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Agent management
    path('', views.AgentListView.as_view(), name='agent-list'),
    path('<int:pk>/', views.AgentDetailView.as_view(), name='agent-detail'),
    
    # Chat functionality
    path('<int:pk>/chat/', views.AgentChatView.as_view(), name='agent-chat'),
    path('<int:pk>/auto-chat/', views.AgentAutoChatView.as_view(), name='agent-auto-chat'),
    
    # Wallet management
    path('<int:pk>/wallet/', views.AgentWalletView.as_view(), name='agent-wallet'),
    
    # Actions and tasks
    path('<int:pk>/actions/', views.AgentActionView.as_view(), name='agent-actions'),
    path('<int:pk>/tasks/', views.AgentTaskView.as_view(), name='agent-tasks'),
    path('actions/', views.AgentAvailableActionsView.as_view(), name='available-actions'),
    
    # Asset management
    path('<int:pk>/tokens/', views.AgentTokenView.as_view(), name='agent-tokens'),
    path('<int:pk>/balance/', views.AgentBalanceView.as_view(), name='agent-balance'),
    path('<int:pk>/test-funds/', views.AgentTestFundsView.as_view(), name='agent-test-funds'),
]
