"""
CoinGecko price action for retrieving cryptocurrency prices.
"""
from typing import Dict, Any, Optional, Callable
from datetime import timedelta
from pycoingecko import CoinGeckoAPI
from django.utils import timezone
from pydantic import BaseModel, ConfigDict
from cdp_agentkit_core.actions import CdpAction
from ..models import PriceCache


class CoinGeckoPriceInput(BaseModel):
    """Input schema for price action"""
    token_id: str
    vs_currencies: Optional[str] = "usd"


class CoinGeckoPriceAction(CdpAction):
    """Action for retrieving cryptocurrency prices from CoinGecko."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "get_token_price"
    description: str = "Get current price for a cryptocurrency token using CoinGecko"
    args_schema: type[BaseModel] = CoinGeckoPriceInput
    
    def __init__(self):
        """Initialize with CoinGecko API client."""
        super().__init__()
        self._cg = CoinGeckoAPI()
        self._cache_duration = timedelta(minutes=5)

    @staticmethod
    async def _execute(parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute the price fetch action"""
        token_id = parameters.get('token_id', '').lower()
        vs_currencies = parameters.get('vs_currencies', 'usd').lower()
        
        try:
            cg = CoinGeckoAPI()
            price_data = cg.get_price(
                ids=token_id,
                vs_currencies=vs_currencies,
                include_24hr_change=True,
                include_last_updated_at=True
            )
            
            if not price_data or token_id not in price_data:
                return {
                    "success": False,
                    "error": f"No price data found for {token_id}"
                }
            
            return {
                "success": True,
                "data": price_data[token_id],
                "source": "api"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get price data: {str(e)}"
            }

    # Set the execute function as the action's func
    func = _execute
