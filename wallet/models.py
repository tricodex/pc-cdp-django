"""
Models for wallet management
"""
from django.db import models
from core.models import TimeStampedModel, Status


class WalletConnection(TimeStampedModel):
    """
    Model to track wallet connections and their status
    """
    address = models.CharField(max_length=255, unique=True)
    chain_id = models.IntegerField()
    last_connected = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    nonce = models.CharField(max_length=255, blank=True)
    signature = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-last_connected']

    def __str__(self):
        return f"{self.address} ({self.chain_id})"


class WalletTransaction(TimeStampedModel):
    """
    Model to track wallet transactions
    """
    wallet = models.ForeignKey(
        WalletConnection,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_hash = models.CharField(max_length=255, unique=True)
    transaction_type = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    data = models.JSONField()
    error_message = models.TextField(blank=True)
    gas_used = models.BigIntegerField(null=True)
    gas_price = models.BigIntegerField(null=True)
    block_number = models.BigIntegerField(null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_hash} ({self.status})"