"""
Custom exceptions for the framework
"""

class CDPConfigurationError(Exception):
    """Raised when CDP client configuration fails"""
    pass


class AgentConfigurationError(Exception):
    """Raised when agent configuration is invalid"""
    pass


class WalletOperationError(Exception):
    """Raised when a wallet operation fails"""
    pass