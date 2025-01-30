"""
Main service manager for agents.
"""
from typing import Optional, Dict, Any, Generator
from django.db import transaction
from core.exceptions import AgentConfigurationError
from ..models import Agent
from .wallet import WalletService
from .chat import ChatService
from .actions import ActionService
import logging
import time

logger = logging.getLogger(__name__)

class DeFiAgentManager:
    """Service manager for DeFi agents."""
    _instance_cache = {}

    def __new__(cls, agent_model: Agent):
        """Ensure single instance per agent"""
        if not agent_model:
            raise AgentConfigurationError("Agent model is required")
            
        if agent_model.id in cls._instance_cache:
            return cls._instance_cache[agent_model.id]
            
        instance = super(DeFiAgentManager, cls).__new__(cls)
        cls._instance_cache[agent_model.id] = instance
        return instance

    def __init__(self, agent_model: Agent):
        """Initialize with an agent model instance"""
        # Skip initialization if already initialized with same agent
        if hasattr(self, 'agent') and self.agent.id == agent_model.id:
            return

        self.agent = agent_model
        self._agentkit = None
        self._services_initialized = False
        
        try:
            self._initialize_services()
        except Exception as e:
            logger.error(f"Failed to initialize services for agent {agent_model.id}: {str(e)}")
            raise

    def _initialize_services(self):
        """Initialize all services in the correct order"""
        if self._services_initialized:
            return

        try:
            # Step 1: Initialize wallet service and get wallet
            self.wallet_service = WalletService(self.agent)
            self.wallet_service.initialize_wallet()
            self._agentkit = self.wallet_service.agentkit

            if not self._agentkit:
                raise AgentConfigurationError("Failed to initialize AgentKit")

            # Step 2: Initialize other services with the AgentKit instance
            self.chat_service = ChatService(self.agent, self._agentkit)
            self.action_service = ActionService(self.agent, self._agentkit)

            self._services_initialized = True

        except Exception as e:
            logger.error(f"Service initialization failed: {str(e)}")
            raise AgentConfigurationError(f"Failed to initialize services: {str(e)}")

    def _ensure_services_initialized(self):
        """Ensure all services are properly initialized"""
        if not self._services_initialized:
            self._initialize_services()

    def get_available_actions(self) -> list:
        """Get list of available CDP actions"""
        self._ensure_services_initialized()
        return self.action_service.get_available_actions()

    @transaction.atomic
    def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CDP action"""
        self._ensure_services_initialized()
        try:
            result = self.action_service.execute_action(action_type, parameters)
            self.wallet_service.update_wallet_data()
            return result
        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            raise

    @transaction.atomic
    def chat_sync(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a chat message synchronously"""
        self._ensure_services_initialized()
        try:
            result = self.chat_service.chat_sync(message, conversation_id)
            self.wallet_service.update_wallet_data()
            return result
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise

    @transaction.atomic
    def stream_chat_sync(self, message: str, conversation_id: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        """Stream chat responses synchronously"""
        self._ensure_services_initialized()
        try:
            async_gen = self.chat_service.stream_chat_sync(message, conversation_id)
            for chunk in async_gen:
                yield chunk
            self.wallet_service.update_wallet_data()
        except Exception as e:
            logger.error(f"Stream chat failed: {str(e)}")
            yield {"error": str(e)}

    def stream_auto_chat(self, message: Optional[str] = None, interval: int = 10, strategy: str = None, conversation_id: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        """Stream auto-chat responses with interval between iterations"""
        self._ensure_services_initialized()
        
        if message is None:
            message = (
                "Choose an action or set of actions and execute it that highlights your abilities."
            )
        
        try:
            while True:
                try:
                    # Get the response using the chat service with specified strategy
                    for chunk in self.chat_service.stream_auto_chat(message, interval, strategy, conversation_id):
                        yield chunk

                    # Update wallet data after each successful interaction
                    try:
                        self.wallet_service.update_wallet_data()
                    except Exception as e:
                        logger.warning(f"Failed to update wallet data: {str(e)}")
                        
                    # Sleep for the specified interval before next iteration
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Auto-chat iteration failed: {str(e)}")
                    yield {"error": f"Auto-chat iteration failed: {str(e)}"}
                    # Still wait before retrying
                    time.sleep(interval)
                    
        except Exception as e:
            logger.error(f"Auto-chat stream failed: {str(e)}")
            yield {"error": str(e)}
