"""
Base functionality for agent services.
"""
from typing import Optional, Dict, Any
from core.cdp_client import CDPClient
from core.exceptions import AgentConfigurationError
from ..models import Agent, AgentWallet
from cdp_langchain.utils import CdpAgentkitWrapper
import logging

logger = logging.getLogger(__name__)

class BaseAgentService:
    """Base class for agent services."""
    _instance_cache = {}  # Cache for service instances
    _agentkit_cache = {}  # Cache for CdpAgentkitWrapper instances

    def __new__(cls, agent_model, agentkit=None):
        """Ensure single instance per agent"""
        if not agent_model:
            raise AgentConfigurationError("Agent model is required")
            
        # Include agentkit in cache key to ensure proper service separation
        cache_key = (agent_model.id, id(agentkit) if agentkit else None)
        
        if cache_key in cls._instance_cache:
            instance = cls._instance_cache[cache_key]
            # Update agentkit if a new one is provided
            if agentkit and instance._agentkit != agentkit:
                instance._agentkit = agentkit
            return instance
            
        instance = super(BaseAgentService, cls).__new__(cls)
        cls._instance_cache[cache_key] = instance
        return instance

    def __init__(self, agent_model: Agent, agentkit: Optional[CdpAgentkitWrapper] = None):
        """Initialize with an agent model instance and optional agentkit"""
        # Skip initialization if already initialized with same agent and agentkit
        if (hasattr(self, 'agent') and self.agent.id == agent_model.id and 
            hasattr(self, '_agentkit') and self._agentkit == agentkit):
            return

        self.agent = agent_model
        self.cdp_client = CDPClient()
        self._agentkit = agentkit
        self._initialized = False

        try:
            # Get or create wallet
            self.wallet = agent_model.wallet
            
            if self._agentkit:
                # Cache the agentkit instance if provided
                self._agentkit_cache[agent_model.id] = agentkit
        except AgentWallet.DoesNotExist:
            self.wallet = None

    def _log_error(self, message: str, error: Exception = None):
        """Log an error with context"""
        error_msg = f"{message} for agent {self.agent.id}"
        if error:
            error_msg += f": {str(error)}"
        logger.error(error_msg)

    @property
    def agentkit(self) -> Optional[CdpAgentkitWrapper]:
        """Get the CDP Agentkit wrapper instance"""
        return self._agentkit

    @agentkit.setter
    def agentkit(self, value: CdpAgentkitWrapper):
        """Set the CDP Agentkit wrapper instance"""
        if value:
            self._agentkit = value
            self._agentkit_cache[self.agent.id] = value
