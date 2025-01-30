"""
Action and task execution views
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
import logging
from concurrent.futures import ThreadPoolExecutor

from core.auth import AgentPermission
from core.throttling import AgentActionThrottle
from ..models import Agent
from ..serializers import AgentActionSerializer
from ..services import DeFiAgentManager

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AgentActionView(views.APIView):
    """Execute agent actions"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def get(self, request, pk):
        """Get action history"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)
        
        actions = agent.actions.all()[:10]
        serializer = AgentActionSerializer(actions, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, pk):
        """Execute an action"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)
        
        if not hasattr(agent, 'wallet'):
            try:
                manager = DeFiAgentManager(agent)
                manager._initialize_wallet()
            except Exception as e:
                logger.error(f"Failed to initialize wallet for action: {str(e)}")
                raise ValidationError("Agent needs a wallet to perform actions. Wallet initialization failed.")
        
        action_type = request.data.get('action_type')
        parameters = request.data.get('parameters', {})
        
        if not action_type:
            raise ValidationError("action_type is required")

        manager = DeFiAgentManager(agent)
        try:
            result = manager.execute_action(action_type, parameters)
            return Response(result)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentAvailableActionsView(views.APIView):
    """List available CDP actions for agents"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def get(self, request):
        """Get list of available actions"""
        manager = DeFiAgentManager(None)
        actions = manager.get_available_actions()
        return Response(actions)


@method_decorator(csrf_exempt, name='dispatch')
class AgentTaskView(views.APIView):
    """Execute agent tasks using LangChain"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def post(self, request, pk):
        """Execute a task"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)
        
        if not hasattr(agent, 'wallet'):
            try:
                manager = DeFiAgentManager(agent)
                manager._initialize_wallet()
            except Exception as e:
                logger.error(f"Failed to initialize wallet for task: {str(e)}")
                raise ValidationError("Agent needs a wallet to perform tasks. Wallet initialization failed.")
        
        task = request.data.get('task')
        if not task:
            raise ValidationError("task description is required")

        manager = DeFiAgentManager(agent)
        try:
            # Run task in thread to avoid blocking
            with ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: async_to_sync(manager.run_agent_task)(task))
                result = future.result()
            return Response(result)
        except Exception as e:
            logger.error(f"Task execution failed for agent {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
