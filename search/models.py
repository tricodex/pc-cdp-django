"""
Search models and document definitions
"""
from django.conf import settings
from elasticsearch_dsl import Document, Date, Text, Keyword, Object, Long, Index, Nested


class WalletDocument(Document):
    """
    Elasticsearch document for wallet data
    """
    address = Keyword()
    chain_id = Long()
    status = Keyword()
    last_connected = Date()
    transactions = Object(
        properties={
            'total_count': Long(),
            'successful_count': Long(),
            'failed_count': Long(),
            'last_transaction_date': Date()
        }
    )
    metadata = Object()

    class Index:
        name = 'wallets'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class AgentDocument(Document):
    """
    Elasticsearch document for agent data
    """
    name = Text(fields={'keyword': Keyword()})
    description = Text()
    status = Keyword()
    wallet_address = Keyword()
    configuration = Object()
    actions = Nested(
        properties={
            'action_type': Keyword(),
            'status': Keyword(),
            'created_at': Date(),
            'parameters': Object(),
            'result': Object()
        }
    )
    created_at = Date()
    updated_at = Date()

    class Index:
        name = 'agents'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class TransactionDocument(Document):
    """
    Elasticsearch document for transaction data
    """
    wallet_address = Keyword()
    transaction_hash = Keyword()
    transaction_type = Keyword()
    status = Keyword()
    block_number = Long()
    gas_used = Long()
    gas_price = Long()
    created_at = Date()
    data = Object()
    error_message = Text()

    class Index:
        name = 'transactions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

# Create indices if they don't exist
def init_indices():
    """
    Initialize Elasticsearch indices
    """
    WalletDocument.init()
    AgentDocument.init()
    TransactionDocument.init()