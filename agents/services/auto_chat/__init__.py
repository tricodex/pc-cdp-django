"""
Auto-chat strategy system.
"""
from .base import AutoChatStrategy
from .trading import TradingStrategy
from .creative import CreativeStrategy

# Register available strategies
AVAILABLE_STRATEGIES = {
    'trading': TradingStrategy,
    'creative': CreativeStrategy,
    'default': AutoChatStrategy
}

__all__ = ['AutoChatStrategy', 'TradingStrategy', 'CreativeStrategy', 'AVAILABLE_STRATEGIES']
