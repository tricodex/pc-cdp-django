"""
CDP client configuration and utilities
"""
from django.conf import settings
from cdp import Cdp, Wallet, WalletData
from core.exceptions import CDPConfigurationError


class CDPClient:
    """
    Singleton class for managing CDP client instance
    """
    _instance = None
    _is_initialized = False
    
    def __init__(self):
        if not CDPClient._is_initialized:
            self._initialize()
            CDPClient._is_initialized = True
        
        if not hasattr(self, 'persistent_wallet'):
            self.persistent_wallet = None
        
        if not hasattr(self, '_wallets'):
            self._wallets = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize(self):
        """
        Initialize CDP client with configuration from settings
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info("Initializing CDP client")
            
            # Get configuration from settings
            api_key_name = getattr(settings, 'CDP_API_KEY_NAME', None)
            api_key_private_key = getattr(settings, 'CDP_API_KEY_PRIVATE_KEY', None)
            
            if not api_key_name or not api_key_private_key:
                raise CDPConfigurationError("Missing CDP API credentials in settings")
            
            # Configure CDP with API credentials
            logger.info("Configuring CDP with API credentials")
            try:
                Cdp.configure(api_key_name, api_key_private_key)
            except Exception as config_error:
                logger.error(f"Failed to configure CDP: {str(config_error)}")
                raise CDPConfigurationError(f"CDP configuration failed: {str(config_error)}")
            
            # Create CDP instance
            try:
                self.cdp = Cdp()
            except Exception as instance_error:
                logger.error(f"Failed to create CDP instance: {str(instance_error)}")
                raise CDPConfigurationError(f"CDP instance creation failed: {str(instance_error)}")
            
            # Set default network
            self._network_id = getattr(settings, 'NETWORK_ID', 'base-sepolia')
            logger.info(f"CDP client initialized with network: {self._network_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CDP client: {str(e)}")
            if hasattr(e, '__cause__') and e.__cause__:
                logger.error(f"Cause: {str(e.__cause__)}")
            raise

    @property
    def network_id(self):
        return self._network_id

    @network_id.setter
    def network_id(self, value):
        self._network_id = value

    def create_wallet(self):
        """
        Create a new Developer-Managed (1-of-1) wallet.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Creating new wallet on network {self.network_id}")
            
            # Create new wallet with specified network
            wallet = Wallet.create(network_id=self.network_id)
            if not wallet:
                raise CDPConfigurationError("Wallet creation returned None")
            
            if not wallet.id:
                raise CDPConfigurationError("Created wallet has no ID")
            
            if not wallet.default_address or not wallet.default_address.address_id:
                raise CDPConfigurationError("Created wallet has no default address")
            
            # Export wallet data for persistence
            try:
                wallet_data = wallet.export_data()
            except Exception as export_error:
                logger.error(f"Failed to export wallet data: {str(export_error)}")
                raise CDPConfigurationError(f"Failed to export wallet data: {str(export_error)}")
            
            # Create persistent wallet data structure
            wallet_info = {
                'id': wallet.id,
                'seed': {
                    'wallet_id': wallet.id,
                    'seed': wallet_data.seed,
                    'network_id': self.network_id
                },
                'default_address': wallet.default_address.address_id,
                'network_id': self.network_id
            }
            
            # Store in both places for backward compatibility
            self.persistent_wallet = wallet_info
            self._wallets[wallet.id] = {
                **wallet_info,
                'wallet': wallet  # Store actual wallet instance only in memory
            }
            
            logger.info(f"Successfully created wallet {wallet.id} with address {wallet.default_address.address_id}")
            return wallet
                
        except Exception as e:
            error_msg = f"Failed to create wallet: {str(e)}"
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg += f" Cause: {str(e.__cause__)}"
            logger.error(error_msg)
            raise CDPConfigurationError(error_msg)

    def import_wallet(self, wallet_data: dict):
        """
        Import an existing wallet from its data.
        Args:
            wallet_data (dict): Dict containing wallet configuration data
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # First check if we already have this wallet
            if wallet_data and 'seed' in wallet_data:
                wallet_id = wallet_data['seed'].get('wallet_id')
                if wallet_id in self._wallets:
                    logger.info(f"Using cached wallet {wallet_id}")
                    return self._wallets[wallet_id]['wallet']
            
            # Validate wallet data
            if not wallet_data or not isinstance(wallet_data, dict):
                raise CDPConfigurationError("Wallet data must be a dictionary")
                
            if 'seed' not in wallet_data:
                raise CDPConfigurationError("Missing seed data in wallet configuration")
            
            # Get seed data
            seed_data = wallet_data['seed']
            wallet_id = seed_data.get('wallet_id')
            seed = seed_data.get('seed')
            network_id = seed_data.get('network_id')
            
            # Validate seed data
            if not wallet_id:
                raise CDPConfigurationError("Missing wallet_id in seed data")
            if not seed:
                raise CDPConfigurationError("Missing seed in seed data")
            if not network_id:
                network_id = self.network_id
            
            logger.info(f"Importing wallet {wallet_id} on network {network_id}")
            
            # Create WalletData instance
            try:
                wallet_data_obj = WalletData(wallet_id, seed, network_id)
            except Exception as data_error:
                logger.error(f"Failed to create WalletData object: {str(data_error)}")
                raise CDPConfigurationError(f"Failed to create WalletData object: {str(data_error)}")
            
            # Import the wallet
            try:
                wallet = Wallet.import_data(wallet_data_obj)
            except Exception as import_error:
                logger.error(f"Failed to import wallet: {str(import_error)}")
                raise CDPConfigurationError(f"Failed to import wallet: {str(import_error)}")
                
            if not wallet:
                raise CDPConfigurationError("Wallet import returned None")
                
            if not wallet.id:
                raise CDPConfigurationError("Imported wallet has no ID")
                
            if not wallet.default_address or not wallet.default_address.address_id:
                raise CDPConfigurationError("Imported wallet has no default address")
            
            # Store the wallet info
            stored_data = {
                'id': wallet.id,
                'seed': {
                    'wallet_id': wallet.id,
                    'seed': seed,
                    'network_id': network_id
                },
                'default_address': wallet.default_address.address_id,
                'network_id': network_id
            }
            
            # Store in both places for backward compatibility
            self.persistent_wallet = stored_data
            self._wallets[wallet.id] = {
                **stored_data,
                'wallet': wallet  # Store actual wallet instance only in memory
            }
            
            logger.info(f"Successfully imported wallet {wallet.id} with address {wallet.default_address.address_id}")
            return wallet
                
        except Exception as e:
            error_msg = f"Failed to import wallet: {str(e)}"
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg += f" Cause: {str(e.__cause__)}"
            logger.error(error_msg)
            raise CDPConfigurationError(error_msg)

    def create_or_load_wallet(self, wallet_data=None):
        """
        Create a new wallet or load existing one using saved data.
        Args:
            wallet_data (dict): Dict containing wallet configuration
        """
        if wallet_data and wallet_data.get('seed'):
            return self.import_wallet(wallet_data)
        return self.create_wallet()

    @property
    def api_client(self):
        """Get the CDP API client instance"""
        return self.cdp