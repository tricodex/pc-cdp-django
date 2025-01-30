# """
# Models for the agent framework
# """
# from django.db import models
# from django.conf import settings
# from core.models import TimeStampedModel, Status
# import uuid
# import logging

# logger = logging.getLogger(__name__)

# class Agent(TimeStampedModel):
#     """
#     Model representing an AI agent instance
#     """
#     name = models.CharField(max_length=255, unique=True)
#     description = models.TextField()
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.INACTIVE
#     )
#     configuration = models.JSONField(default=dict)
#     wallet_address = models.CharField(max_length=255, blank=True)
#     owner = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='agents'
#     )
#     eliza_endpoint = models.URLField(
#         max_length=255, 
#         blank=True, 
#         help_text="Endpoint for the agent's Eliza API"
#     )
    
#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.name} ({self.status})"

#     def cleanup(self):
#         """Clean up all associated resources before deletion"""
#         try:
#             if hasattr(self, 'wallet'):
#                 self.wallet.delete()
#             self.actions.all().delete()
#             self.agent_messages.all().delete()
#         except Exception as e:
#             logger.error(f"Error during agent cleanup {self.id}: {str(e)}")
#             raise

#     def delete(self, *args, **kwargs):
#         """Override delete to cleanup associated resources"""
#         self.cleanup()
#         return super().delete(*args, **kwargs)

# class Room(TimeStampedModel):
#     """Model for managing conversation rooms between agents"""
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     chain_id = models.IntegerField(help_text="Blockchain network ID")
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.ACTIVE
#     )
#     configuration = models.JSONField(default=dict)
    
#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.name} ({self.chain_id})"

# class Round(TimeStampedModel):
#     """Model for managing conversation rounds within a room"""
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='rounds')
#     round_number = models.IntegerField()
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.ACTIVE
#     )
#     start_time = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     configuration = models.JSONField(default=dict)
#     gm_actions = models.JSONField(default=list)
#     pvp_actions = models.JSONField(default=list)

#     class Meta:
#         ordering = ['room', 'round_number']
#         unique_together = ['room', 'round_number']

#     def __str__(self):
#         return f"Round {self.round_number} - {self.room.name}"

# class RoundAgentMessage(TimeStampedModel):
#     """Model for storing messages between agents in a round"""
#     round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='agent_messages')
#     sender = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='sent_messages')
#     timestamp = models.DateTimeField()
#     signature = models.CharField(max_length=255)
#     content = models.JSONField()
    
#     class Meta:
#         ordering = ['timestamp']
#         indexes = [
#             models.Index(fields=['round', 'timestamp']),
#             models.Index(fields=['sender', 'timestamp'])
#         ]

#     def __str__(self):
#         return f"Message from {self.sender.name} in Round {self.round.round_number}"

# class RoomAgent(TimeStampedModel):
#     """Model for managing agent participation in rooms"""
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_agents')
#     agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='room_memberships')
#     is_gm = models.BooleanField(default=False, help_text="Whether the agent is a game master")
#     joined_at = models.DateTimeField(auto_now_add=True)
#     configuration = models.JSONField(default=dict)

#     class Meta:
#         unique_together = ['room', 'agent']
#         ordering = ['joined_at']

#     def __str__(self):
#         return f"{self.agent.name} in {self.room.name}"

# class AgentAction(TimeStampedModel):
#     """Model for tracking agent actions and their results"""
#     agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='actions')
#     action_type = models.CharField(max_length=100)
#     parameters = models.JSONField(default=dict)
#     result = models.JSONField(null=True, blank=True)
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING
#     )
#     error_message = models.TextField(blank=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.agent.name} - {self.action_type} ({self.status})"

# class AgentWallet(TimeStampedModel):
#     """Model for managing agent wallet configurations"""
#     agent = models.OneToOneField(Agent, on_delete=models.CASCADE, related_name='wallet')
#     wallet_id = models.CharField(max_length=255, unique=True)
#     network_id = models.CharField(max_length=100)
#     address = models.CharField(max_length=255)
#     configuration = models.JSONField(default=dict)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Wallet for {self.agent.name} ({self.network_id})"

# class TokenPrice(TimeStampedModel):
#     """Stores historical cryptocurrency price data"""
#     token_id = models.CharField(max_length=100)
#     price_usd = models.DecimalField(max_digits=24, decimal_places=12)
#     price_eth = models.DecimalField(max_digits=24, decimal_places=12, null=True)
#     market_cap_usd = models.DecimalField(max_digits=24, decimal_places=2, null=True)
#     volume_24h_usd = models.DecimalField(max_digits=24, decimal_places=2, null=True)
#     change_24h = models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     timestamp = models.DateTimeField()

#     class Meta:
#         indexes = [
#             models.Index(fields=['token_id']),
#             models.Index(fields=['timestamp']),
#             models.Index(fields=['token_id', 'timestamp'])
#         ]
#         get_latest_by = 'timestamp'

# class PriceCache(TimeStampedModel):
#     """Cache for storing cryptocurrency price data"""
#     token_id = models.CharField(max_length=100)
#     price_data = models.JSONField()
#     expires_at = models.DateTimeField()

#     class Meta:
#         indexes = [
#             models.Index(fields=['token_id']),
#             models.Index(fields=['expires_at'])
#         ]

# class ChatMessage(TimeStampedModel):
#     """Model for storing chat messages between users and agents"""
#     class MessageType(models.TextChoices):
#         HUMAN = 'human', 'Human'
#         AI = 'ai', 'AI'
#         TOOL = 'tool', 'Tool'
#         SYSTEM = 'system', 'System'
    
#     agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='chat_messages')
#     message_type = models.CharField(max_length=10, choices=MessageType.choices)
#     content = models.TextField()
#     metadata = models.JSONField(default=dict, help_text='Additional message metadata like tool calls or system info')
#     parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
#     conversation_id = models.UUIDField(default=uuid.uuid4, help_text='Groups messages in same conversation')
    
#     class Meta:
#         ordering = ['created_at']
#         indexes = [
#             models.Index(fields=['agent', 'conversation_id']),
#             models.Index(fields=['conversation_id']),
#             models.Index(fields=['created_at'])
#         ]

#     def __str__(self):
#         return f"{self.agent.name} - {self.message_type} ({self.created_at})"