"""
Rate limiting and throttling utilities
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AgentActionThrottle(UserRateThrottle):
    """
    Throttle for agent actions
    """
    rate = '100/hour'
    scope = 'agent_actions'


class WalletOperationThrottle(UserRateThrottle):
    """
    Throttle for wallet operations
    """
    rate = '50/hour'
    scope = 'wallet_operations'


class DocumentationSearchThrottle(AnonRateThrottle):
    """
    Throttle for documentation search
    """
    rate = '30/hour'
    scope = 'documentation_search'