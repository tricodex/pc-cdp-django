"""
Wallet management services for agents.
"""
from typing import Optional, Dict, Any
from django.db import transaction
from core.exceptions import AgentConfigurationError
from cdp_langchain.utils import CdpAgentkitWrapper
from ..models import AgentWallet
from .base import BaseAgentService
import logging

logger = logging.getLogger(__name__)

class WalletService(BaseAgentService):
    """Service for managing agent wallets."""
    
    @transaction.atomic
    def initialize_wallet(self) -> Optional[AgentWallet]:
        """Initialize or get existing wallet for the agent"""
        try:
            try:
                # Try to get existing wallet from database
                self.wallet = self.agent.wallet
                
                # Check if we have a cached agentkit instance
                if self.agent.id in self._agentkit_cache:
                    self.agentkit = self._agentkit_cache[self.agent.id]
                    return self.wallet

                # Get wallet data and network info
                wallet_data = self.wallet.configuration.get('cdp_wallet_data')
                network_id = self.wallet.network_id
                
                # Initialize CDP Agentkit with wallet data
                values = {}
                if wallet_data:
                    values = {"cdp_wallet_data": wallet_data}
                
                # Create CDP Agentkit wrapper
                self._agentkit = CdpAgentkitWrapper(
                    agent_id=str(self.agent.id),
                    wallet_id=self.wallet.wallet_id,
                    wallet_address=self.wallet.address,
                    network_id=network_id,
                    **values
                )
                
                # Export updated wallet data and store it
                updated_wallet_data = self._agentkit.export_wallet()
                wallet_config = self.wallet.configuration
                wallet_config['cdp_wallet_data'] = updated_wallet_data
                self.wallet.configuration = wallet_config
                self.wallet.save()

                # Cache the agentkit instance
                self.agentkit = self._agentkit
                
                return self.wallet
                
            except AgentWallet.DoesNotExist:
                # Get network_id from configuration or use default
                network_id = (
                    self.agent.configuration.get('network_id') or
                    self.agent.configuration.get('network') or
                    'base-sepolia'
                )
                
                # Create new CDP Agentkit wrapper
                self._agentkit = CdpAgentkitWrapper(
                    agent_id=str(self.agent.id),
                    network_id=network_id
                )
                
                # Export wallet data
                wallet_data = self._agentkit.export_wallet()
                
                # Create persistent data structure
                wallet_config = {
                    'cdp_wallet_data': wallet_data,
                    'network_id': network_id,
                    'wallet_id': self._agentkit.wallet.id,
                    'address': self._agentkit.wallet.default_address.address_id
                }
                
                # Create wallet record in database
                self.wallet = AgentWallet.objects.create(
                    agent=self.agent,
                    wallet_id=self._agentkit.wallet.id,
                    network_id=network_id,
                    address=self._agentkit.wallet.default_address.address_id,
                    configuration=wallet_config
                )
                
                # Update agent with wallet address
                self.agent.wallet_address = self._agentkit.wallet.default_address.address_id
                self.agent.save()
                
                # Cache the agentkit instance
                self.agentkit = self._agentkit
                
                return self.wallet

        except Exception as e:
            self._log_error("Failed to initialize wallet", e)
            raise AgentConfigurationError(f"Failed to initialize wallet: {str(e)}")

    @transaction.atomic
    def update_wallet_data(self):
        """Update wallet data in database after operations"""
        if self._agentkit and hasattr(self, 'wallet'):
            try:
                updated_wallet_data = self._agentkit.export_wallet()
                wallet_config = self.wallet.configuration
                wallet_config['cdp_wallet_data'] = updated_wallet_data
                self.wallet.configuration = wallet_config
                self.wallet.save()
            except Exception as e:
                self._log_error("Failed to update wallet data", e)
                raise AgentConfigurationError(f"Failed to update wallet data: {str(e)}")
