"""
Custom agent actions
"""
from cdp_agentkit_core.actions import CDP_ACTIONS
from .documentation_action import DocumentationSearchAction
from .price_action_storage import StoragePriceAction
from .price_action import CoinGeckoPriceAction
from .websearch import WebSearchAction

# Add custom actions to the CDP actions list
CUSTOM_ACTIONS = [
    DocumentationSearchAction(),
    StoragePriceAction(),
    CoinGeckoPriceAction(),
    WebSearchAction()
]

# Combine standard CDP actions with custom actions
ALL_ACTIONS = CDP_ACTIONS + CUSTOM_ACTIONS

__all__ = ['ALL_ACTIONS', 'CUSTOM_ACTIONS', 'DocumentationSearchAction', 'StoragePriceAction', 'CoinGeckoPriceAction', 'WebSearchAction']
