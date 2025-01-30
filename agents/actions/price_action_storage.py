"""
CoinGecko price action with historical storage for retrieving cryptocurrency prices.
"""
from typing import Dict, Any, Optional, Callable
from datetime import timedelta
from django.utils import timezone
from pydantic import BaseModel, ConfigDict
from cdp_agentkit_core.actions import CdpAction
from ..services.auto_chat.data.price_fetcher import PriceFetcher


class StoragePriceInput(BaseModel):
    """Input schema for price storage action"""
    token_id: str
    include_history: Optional[bool] = False
    hours: Optional[int] = 24


class StoragePriceAction(CdpAction):
    """Action for retrieving cryptocurrency prices with historical storage."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "get_token_price_storage"
    description: str = (
        "Get current and historical price data for a cryptocurrency token "
        "using stored data and CoinGecko API"
    )
    args_schema: type[BaseModel] = StoragePriceInput

    @staticmethod
    async def _execute(parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute the price fetch action"""
        token_id = parameters.get('token_id', '').lower()
        include_history = parameters.get('include_history', False)
        hours = parameters.get('hours', 24)
        
        try:
            fetcher = PriceFetcher()
            fetcher.tokens = [token_id]
            
            # Get latest price
            current_data = fetcher.get_latest_prices()
            if not current_data["success"]:
                return current_data
            
            result = {
                "success": True,
                "current": current_data["data"].get(token_id, {}),
                "timestamp": current_data["timestamp"]
            }
            
            # Include historical data if requested
            if include_history:
                end_time = timezone.now()
                start_time = end_time - timedelta(hours=hours)
                
                history = fetcher.get_historical_prices(
                    token_id,
                    start_time=start_time,
                    end_time=end_time
                )
                
                result["history"] = [{
                    "timestamp": price.timestamp.isoformat(),
                    "price_usd": float(price.price_usd),
                    "price_eth": float(price.price_eth) if price.price_eth else None,
                    "market_cap_usd": float(price.market_cap_usd) if price.market_cap_usd else None,
                    "volume_24h_usd": float(price.volume_24h_usd) if price.volume_24h_usd else None,
                    "change_24h": float(price.change_24h) if price.change_24h else None
                } for price in history]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get price data: {str(e)}"
            }

    # Set the execute function as the action's func
    func = _execute
