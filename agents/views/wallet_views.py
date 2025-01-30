"""
Wallet management views
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from core.auth import AgentPermission
from core.throttling import AgentActionThrottle
from ..models import Agent, AgentWallet
from ..serializers import AgentWalletSerializer
from ..services import DeFiAgentManager

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AgentWalletView(views.APIView):
    """Create or manage agent wallet"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    @transaction.atomic
    def post(self, request, pk):
        """Create a wallet for the agent"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)

        if hasattr(agent, 'wallet'):
            raise ValidationError("Agent already has a wallet")

        try:
            manager = DeFiAgentManager(agent)
            wallet = manager._initialize_wallet()
            return Response({
                'wallet_id': wallet.id,
                'address': wallet.default_address.address_id,
                'network': manager.cdp_client.network_id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Wallet creation failed: {str(e)}")
            raise ValidationError(f"Failed to create wallet: {str(e)}")

    def get(self, request, pk):
        """Get wallet details"""
        agent = get_object_or_404(Agent, pk=pk)
        self.check_object_permissions(request, agent)

        try:
            wallet = agent.wallet
            serializer = AgentWalletSerializer(wallet)
            return Response(serializer.data)
        except AgentWallet.DoesNotExist:
            return Response(
                {"detail": "Agent has no wallet"}, 
                status=status.HTTP_404_NOT_FOUND
            )
