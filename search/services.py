"""
Search services
"""
from elasticsearch_dsl import Q, Search
from typing import List, Dict, Any
from .models import WalletDocument, AgentDocument, TransactionDocument


class SearchService:
    """
    Service for handling search operations
    """
    @staticmethod
    def search_wallets(query: str = None, filters: Dict = None, page: int = 1, size: int = 10) -> dict:
        """
        Search wallet documents
        """
        s = Search(index='wallets')
        
        # Apply text search if query provided
        if query:
            s = s.query('multi_match', query=query, fields=['address^3', 'metadata.*'])
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if value is not None:
                    s = s.filter('term', **{field: value})
        
        # Pagination
        start = (page - 1) * size
        s = s[start:start + size]
        
        # Execute search
        response = s.execute()
        
        return {
            'total': response.hits.total.value,
            'wallets': [hit.to_dict() for hit in response],
            'page': page,
            'size': size
        }

    @staticmethod
    def search_agents(query: str = None, filters: Dict = None, page: int = 1, size: int = 10) -> dict:
        """
        Search agent documents
        """
        s = Search(index='agents')
        
        # Apply text search if query provided
        if query:
            s = s.query('multi_match', query=query, 
                       fields=['name^3', 'description', 'wallet_address'])
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if value is not None:
                    s = s.filter('term', **{field: value})
        
        # Pagination
        start = (page - 1) * size
        s = s[start:start + size]
        
        # Execute search
        response = s.execute()
        
        return {
            'total': response.hits.total.value,
            'agents': [hit.to_dict() for hit in response],
            'page': page,
            'size': size
        }

    @staticmethod
    def search_transactions(query: str = None, filters: Dict = None, page: int = 1, size: int = 10) -> dict:
        """
        Search transaction documents
        """
        s = Search(index='transactions')
        
        # Apply text search if query provided
        if query:
            s = s.query('multi_match', query=query,
                       fields=['transaction_hash^3', 'wallet_address', 'transaction_type'])
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if value is not None:
                    s = s.filter('term', **{field: value})
        
        # Default sorting by created_at desc
        s = s.sort('-created_at')
        
        # Pagination
        start = (page - 1) * size
        s = s[start:start + size]
        
        # Execute search
        response = s.execute()
        
        return {
            'total': response.hits.total.value,
            'transactions': [hit.to_dict() for hit in response],
            'page': page,
            'size': size
        }

    @staticmethod
    def get_wallet_analytics(wallet_address: str) -> dict:
        """
        Get analytics for a specific wallet
        """
        # Get wallet document
        try:
            wallet_doc = WalletDocument.get(id=wallet_address)
            
            # Get recent transactions
            s = Search(index='transactions')
            s = s.filter('term', wallet_address=wallet_address)
            s = s.sort('-created_at')
            s = s[:5]
            recent_transactions = s.execute()
            
            return {
                'wallet': wallet_doc.to_dict(),
                'recent_transactions': [hit.to_dict() for hit in recent_transactions],
                'transaction_stats': wallet_doc.transactions
            }
        except Exception:
            return None

    @staticmethod
    def get_agent_analytics(agent_id: str) -> dict:
        """
        Get analytics for a specific agent
        """
        try:
            agent_doc = AgentDocument.get(id=agent_id)
            
            # Calculate action statistics
            action_stats = {
                'total': len(agent_doc.actions),
                'by_status': {},
                'by_type': {}
            }
            
            for action in agent_doc.actions:
                # Count by status
                if action.status not in action_stats['by_status']:
                    action_stats['by_status'][action.status] = 0
                action_stats['by_status'][action.status] += 1
                
                # Count by type
                if action.action_type not in action_stats['by_type']:
                    action_stats['by_type'][action.action_type] = 0
                action_stats['by_type'][action.action_type] += 1
            
            return {
                'agent': agent_doc.to_dict(),
                'action_stats': action_stats
            }
        except Exception:
            return None