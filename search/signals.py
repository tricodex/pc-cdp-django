"""
Signals for automatic indexing
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from wallet.models import WalletConnection, WalletTransaction
from agents.models import Agent
from .indexers import WalletIndexer, AgentIndexer, TransactionIndexer


@receiver(post_save, sender=WalletConnection)
def index_wallet(sender, instance, created, **kwargs):
    """Index wallet on save"""
    if created:
        WalletIndexer.index_wallet(instance)
    else:
        WalletIndexer.update_wallet(instance)


@receiver(post_save, sender=Agent)
def index_agent(sender, instance, created, **kwargs):
    """Index agent on save"""
    if created:
        AgentIndexer.index_agent(instance)
    else:
        AgentIndexer.update_agent(instance)


@receiver(post_save, sender=WalletTransaction)
def index_transaction(sender, instance, created, **kwargs):
    """Index transaction on save"""
    if created:
        TransactionIndexer.index_transaction(instance)
    else:
        TransactionIndexer.update_transaction(instance)