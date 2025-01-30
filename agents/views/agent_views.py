"""
Basic agent CRUD views
"""
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from django.db import transaction
import logging

from core.auth import AgentPermission
from core.throttling import AgentActionThrottle
from ..models import Agent
from ..serializers import AgentSerializer
from ..services import DeFiAgentManager

logger = logging.getLogger(__name__)


class AgentListView(generics.ListCreateAPIView):
    """List and create agents"""
    serializer_class = AgentSerializer
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def get_queryset(self):
        """Filter agents by owner"""
        if self.request.user.is_staff:
            return Agent.objects.all()
        return Agent.objects.filter(owner=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        """Create agent with owner and initialize its wallet"""
        try:
            agent = serializer.save(owner=self.request.user)
            manager = DeFiAgentManager(agent)
            try:
                manager._initialize_wallet()
            except Exception as wallet_error:
                logger.error(f"Wallet initialization failed for agent {agent.id}: {str(wallet_error)}")
            return agent
        except Exception as e:
            logger.error(f"Agent creation failed: {str(e)}")
            raise ValidationError(f"Failed to create agent: {str(e)}")


class AgentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an agent"""
    serializer_class = AgentSerializer
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]

    def get_queryset(self):
        """Filter agents by owner"""
        if self.request.user.is_staff:
            return Agent.objects.all()
        return Agent.objects.filter(owner=self.request.user)

    @transaction.atomic
    def perform_destroy(self, instance):
        """Delete agent and all associated resources"""
        try:
            instance.delete()
        except Exception as e:
            logger.error(f"Agent deletion failed: {str(e)}")
            raise ValidationError(f"Failed to delete agent: {str(e)}")
