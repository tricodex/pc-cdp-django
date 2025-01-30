"""
Action-related services for agents.
"""
from typing import Dict, Any, List, Optional
from django.db import transaction
from core.exceptions import AgentConfigurationError
from cdp_agentkit_core.actions import CDP_ACTIONS
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from ..models import AgentAction
from .base import BaseAgentService
import logging

logger = logging.getLogger(__name__)

class ActionService(BaseAgentService):
    """Service for managing agent actions."""
    
    def __init__(self, agent_model, agentkit: Optional[CdpAgentkitWrapper] = None):
        """Initialize action service"""
        super().__init__(agent_model, agentkit)
        self._toolkit = None

    def _ensure_toolkit_initialized(self):
        """Ensure CDP toolkit is initialized"""
        if not self._toolkit:
            if not self.agentkit:
                raise AgentConfigurationError("CDP Agentkit wrapper not initialized")
            self._toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.agentkit)

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available CDP actions"""
        return [
            {
                'name': action.name,
                'description': action.description,
                'schema': action.args_schema.schema() if action.args_schema else None
            }
            for action in CDP_ACTIONS
        ]

    @transaction.atomic
    def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CDP action"""
        if not self.agentkit:
            raise AgentConfigurationError("CDP Agentkit wrapper not initialized")

        # Initialize toolkit if needed
        self._ensure_toolkit_initialized()

        # Find the appropriate tool
        tool = next((t for t in self._toolkit.get_tools() if t.name == action_type), None)
        if not tool:
            raise AgentConfigurationError(f"Action {action_type} not found")

        # Add necessary context to parameters
        parameters = {
            'agent_id': str(self.agent.id),
            'wallet_id': self.wallet.wallet_id,
            'wallet_address': self.wallet.address,
            'network_id': self.wallet.network_id,
            **parameters
        }

        # Create action record
        action = AgentAction.objects.create(
            agent=self.agent,
            action_type=action_type,
            parameters=parameters,
            status='pending'
        )

        try:
            # Execute the action
            result = tool.run(parameters)
            
            # Update action record with success
            action.status = 'completed'
            action.result = {'status': 'success', 'data': result}
            action.save()
            
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            # Update action record with error
            action.status = 'error'
            action.result = {'status': 'error', 'error': str(e)}
            action.error_message = str(e)
            action.save()
            
            self._log_error(f"Action {action_type} failed", e)
            raise AgentConfigurationError(str(e))
