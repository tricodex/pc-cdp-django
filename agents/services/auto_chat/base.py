"""
Base auto-chat strategy.
"""
from typing import Dict, Any, Optional, Generator
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class AutoChatStrategy(ABC):
    """Base class for auto-chat strategies."""
    
    def __init__(self, agent, interval: int = 30):
        """Initialize the strategy."""
        self.agent = agent
        self.interval = interval
        self._stop = False
        self.context = {
            'conversation_history': [],
            'iteration_count': 0,
            'last_message_id': None,
            'current_conversation_id': None
        }
        
    @property
    def name(self) -> str:
        """Get strategy name."""
        return self.__class__.__name__
        
    def generate_message(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate the next message to send."""
        return (
            "Be creative and do something interesting on the blockchain. "
            "Choose an action or set of actions and execute it that highlights your abilities."
        )
        
    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process the response from the agent."""
        return response
        
    def should_continue(self) -> bool:
        """Check if the strategy should continue running."""
        return not self._stop
        
    def stop(self):
        """Stop the strategy."""
        self._stop = True

    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self.context

    def update_context(self, data: Dict[str, Any]):
        """Update strategy context."""
        self.context.update(data)
