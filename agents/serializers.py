"""
Serializers for the agents app
"""
from rest_framework import serializers
from .models import Agent, AgentAction, AgentWallet, ChatMessage


class AgentWalletSerializer(serializers.ModelSerializer):
    """
    Serializer for agent wallets
    """
    class Meta:
        model = AgentWallet
        fields = ['id', 'wallet_id', 'network_id', 'address', 'is_active', 'created_at']
        read_only_fields = ['wallet_id', 'address']


class AgentActionSerializer(serializers.ModelSerializer):
    """
    Serializer for agent actions
    """
    class Meta:
        model = AgentAction
        fields = ['id', 'agent', 'action_type', 'parameters', 'result', 
                 'status', 'error_message', 'created_at']
        read_only_fields = ['result', 'status', 'error_message']


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages
    """
    class Meta:
        model = ChatMessage
        fields = ['id', 'agent', 'message_type', 'content', 'metadata',
                 'parent_message', 'conversation_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class AgentSerializer(serializers.ModelSerializer):
    """
    Serializer for agents
    """
    wallet = AgentWalletSerializer(read_only=True)
    recent_actions = AgentActionSerializer(many=True, read_only=True, source='actions')
    recent_messages = ChatMessageSerializer(many=True, read_only=True, source='chat_messages')

    class Meta:
        model = Agent
        fields = ['id', 'name', 'description', 'status', 'configuration',
                 'wallet_address', 'wallet', 'recent_actions', 'recent_messages', 'created_at']
        read_only_fields = ['wallet_address']

    def to_representation(self, instance):
        """
        Limit the number of recent actions and messages shown
        """
        data = super().to_representation(instance)
        data['recent_actions'] = data['recent_actions'][:5]  # Only show 5 most recent actions
        data['recent_messages'] = data['recent_messages'][:10]  # Show 10 most recent messages
        return data