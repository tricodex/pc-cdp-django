"""
Services for wallet management
"""
import secrets
from eth_account.messages import encode_defunct
from web3 import Web3
from core.cdp_client import CDPClient
from core.exceptions import WalletOperationError
from .models import WalletConnection, WalletTransaction


class WalletManager:
    """
    Service class for managing wallet operations
    """
    def __init__(self):
        self.cdp_client = CDPClient()
        self.w3 = Web3()

    def create_connection_challenge(self, address: str, chain_id: int) -> dict:
        """
        Create a challenge for wallet connection verification
        """
        nonce = secrets.token_hex(32)
        message = f"Sign this message to connect your wallet\nNonce: {nonce}"
        
        # Create or update wallet connection
        wallet_conn, _ = WalletConnection.objects.update_or_create(
            address=address,
            defaults={
                'chain_id': chain_id,
                'nonce': nonce,
                'status': 'pending'
            }
        )
        
        return {
            'message': message,
            'nonce': nonce
        }

    def verify_connection(self, address: str, signature: str) -> WalletConnection:
        """
        Verify wallet connection using signature
        """
        try:
            wallet_conn = WalletConnection.objects.get(address=address)
            
            # Verify signature
            message = encode_defunct(text=f"Sign this message to connect your wallet\nNonce: {wallet_conn.nonce}")
            recovered_address = self.w3.eth.account.recover_message(message, signature=signature)
            
            if recovered_address.lower() != address.lower():
                raise WalletOperationError("Invalid signature")
            
            # Update wallet connection
            wallet_conn.status = 'active'
            wallet_conn.signature = signature
            wallet_conn.save()
            
            return wallet_conn
            
        except WalletConnection.DoesNotExist:
            raise WalletOperationError("Wallet connection not found")
        except Exception as e:
            raise WalletOperationError(f"Verification failed: {str(e)}")

    def get_transactions(self, wallet_connection: WalletConnection, limit: int = 10) -> list:
        """
        Get recent transactions for a wallet
        """
        return wallet_connection.transactions.all()[:limit]

    def create_transaction(self, 
                         wallet_connection: WalletConnection,
                         transaction_type: str,
                         transaction_data: dict) -> WalletTransaction:
        """
        Create and track a new transaction
        """
        return WalletTransaction.objects.create(
            wallet=wallet_connection,
            transaction_type=transaction_type,
            data=transaction_data,
            status='pending'
        )

    def update_transaction_status(self,
                                transaction: WalletTransaction,
                                status: str,
                                **kwargs) -> WalletTransaction:
        """
        Update transaction status and details
        """
        transaction.status = status
        
        # Update optional fields if provided
        for field, value in kwargs.items():
            if hasattr(transaction, field):
                setattr(transaction, field, value)
        
        transaction.save()
        return transaction

    async def sync_transaction_status(self, transaction: WalletTransaction):
        """
        Sync transaction status with blockchain
        """
        try:
            # Get transaction details from CDP API
            wallet_client = self.cdp_client.get_wallet_client()
            tx_details = await wallet_client.get_transaction(transaction.transaction_hash)
            
            # Update status based on chain data
            status = 'completed' if tx_details.get('confirmed') else 'pending'
            self.update_transaction_status(
                transaction,
                status=status,
                block_number=tx_details.get('blockNumber'),
                gas_used=tx_details.get('gasUsed'),
                gas_price=tx_details.get('gasPrice')
            )
            
        except Exception as e:
            self.update_transaction_status(
                transaction,
                status='error',
                error_message=str(e)
            )