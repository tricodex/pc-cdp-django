"""
Token and balance management views
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
import logging
from concurrent.futures import ThreadPoolExecutor

from core.auth import AgentPermission
from core.throttling import AgentActionThrottle
from ..models import Agent
from ..services import DeFiAgentManager

logger = logging.getLogger(__name__)


class AgentTokenView(views.APIView):
    """View for token management"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def get(self, request, pk):
        """Get token information"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)
        
        if not hasattr(agent, 'wallet'):
            try:
                manager = DeFiAgentManager(agent)
                manager._initialize_wallet()
            except Exception as e:
                logger.error(f"Failed to initialize wallet for token view: {str(e)}")
                return Response(
                    {"error": "Agent has no wallet and wallet initialization failed"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Use CDP toolkit to get token information
        manager = DeFiAgentManager(agent)
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: async_to_sync(manager._agentkit.get_tokens)())
                tokens = future.result()
            return Response({"tokens": tokens})
        except Exception as e:
            logger.error(f"Failed to get tokens for agent {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentBalanceView(views.APIView):
    """View for balance information"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def get(self, request, pk):
        """Get balance information"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)
        
        if not hasattr(agent, 'wallet'):
            try:
                manager = DeFiAgentManager(agent)
                manager._initialize_wallet()
            except Exception as e:
                logger.error(f"Failed to initialize wallet for balance view: {str(e)}")
                return Response(
                    {"error": "Agent has no wallet and wallet initialization failed"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Use CDP toolkit to get balance information
        manager = DeFiAgentManager(agent)
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: async_to_sync(manager._agentkit.get_balance)())
                balance = future.result()
            return Response({"balance": balance})
        except Exception as e:
            logger.error(f"Failed to get balance for agent {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class AgentTestFundsView(views.APIView):
    """View for handling test funds"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def post(self, request, pk):
        """Request test funds"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)
        
        if not hasattr(agent, 'wallet'):
            try:
                manager = DeFiAgentManager(agent)
                manager._initialize_wallet()
            except Exception as e:
                logger.error(f"Failed to initialize wallet for test funds: {str(e)}")
                return Response(
                    {"error": "Agent has no wallet and wallet initialization failed"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        try:
            # Run faucet request in thread to avoid blocking
            manager = DeFiAgentManager(agent)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: async_to_sync(manager._agentkit.request_test_funds)())
                result = future.result()
            return Response({"status": "test funds requested", "result": result})
        except Exception as e:
            logger.error(f"Failed to request test funds for agent {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
