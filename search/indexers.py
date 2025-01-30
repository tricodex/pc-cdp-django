"""
Data indexers for Elasticsearch
"""
from datetime import datetime
from elasticsearch_dsl import Q
from wallet.models import WalletConnection, WalletTransaction
from agents.models import Agent, AgentAction
from .models import WalletDocument, AgentDocument, TransactionDocument


class WalletIndexer:
    """
    Indexer for wallet data
    """
    @staticmethod
    def index_wallet(wallet: WalletConnection):
        """Index a single wallet"""
        # Calculate transaction statistics
        transactions = wallet.transactions.all()
        successful_txs = transactions.filter(status='completed').count()
        failed_txs = transactions.filter(status='error').count()
        last_tx = transactions.order_by('-created_at').first()

        doc = WalletDocument(
            meta={'id': wallet.address},
            address=wallet.address,
            chain_id=wallet.chain_id,
            status=wallet.status,
            last_connected=wallet.last_connected,
            transactions={
                'total_count': transactions.count(),
                'successful_count': successful_txs,
                'failed_count': failed_txs,
                'last_transaction_date': last_tx.created_at if last_tx else None
            },
            metadata=wallet.metadata
        )
        doc.save()
        return doc

    @staticmethod
    def update_wallet(wallet: WalletConnection):
        """Update existing wallet document"""
        try:
            doc = WalletDocument.get(id=wallet.address)
            return WalletIndexer.index_wallet(wallet)
        except Exception:
            return WalletIndexer.index_wallet(wallet)


class AgentIndexer:
    """
    Indexer for agent data
    """
    @staticmethod
    def index_agent(agent: Agent):
        """Index a single agent"""
        doc = AgentDocument(
            meta={'id': agent.id},
            name=agent.name,
            description=agent.description,
            status=agent.status,
            wallet_address=agent.wallet_address,
            configuration=agent.configuration,
            actions=[{
                'action_type': action.action_type,
                'status': action.status,
                'created_at': action.created_at,
                'parameters': action.parameters,
                'result': action.result
            } for action in agent.actions.all()],
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
        doc.save()
        return doc

    @staticmethod
    def update_agent(agent: Agent):
        """Update existing agent document"""
        try:
            doc = AgentDocument.get(id=agent.id)
            return AgentIndexer.index_agent(agent)
        except Exception:
            return AgentIndexer.index_agent(agent)


class TransactionIndexer:
    """
    Indexer for transaction data
    """
    @staticmethod
    def index_transaction(transaction: WalletTransaction):
        """Index a single transaction"""
        doc = TransactionDocument(
            meta={'id': transaction.transaction_hash},
            wallet_address=transaction.wallet.address,
            transaction_hash=transaction.transaction_hash,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            block_number=transaction.block_number,
            gas_used=transaction.gas_used,
            gas_price=transaction.gas_price,
            created_at=transaction.created_at,
            data=transaction.data,
            error_message=transaction.error_message
        )
        doc.save()
        return doc

    @staticmethod
    def update_transaction(transaction: WalletTransaction):
        """Update existing transaction document"""
        try:
            doc = TransactionDocument.get(id=transaction.transaction_hash)
            return TransactionIndexer.index_transaction(transaction)
        except Exception:
            return TransactionIndexer.index_transaction(transaction)