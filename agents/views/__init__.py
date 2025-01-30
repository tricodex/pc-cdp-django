"""
Views package for agent management
"""
from .agent_views import AgentListView, AgentDetailView
from .wallet_views import AgentWalletView
from .chat_views import AgentChatView, AgentAutoChatView
from .action_views import (
    AgentActionView,
    AgentAvailableActionsView,
    AgentTaskView
)
from .asset_views import (
    AgentTokenView,
    AgentBalanceView,
    AgentTestFundsView
)

__all__ = [
    'AgentListView',
    'AgentDetailView',
    'AgentWalletView',
    'AgentChatView',
    'AgentAutoChatView',
    'AgentActionView',
    'AgentAvailableActionsView',
    'AgentTaskView',
    'AgentTokenView',
    'AgentBalanceView',
    'AgentTestFundsView',
]
