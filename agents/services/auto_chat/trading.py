from typing import Dict, Any, Optional
from datetime import timedelta
from django.utils import timezone
from .base import AutoChatStrategy
import json
import logging

logger = logging.getLogger(__name__)

class TradingStrategy(AutoChatStrategy):
    """Trading strategy for auto-chat."""
    
    def __init__(self, agent, interval: int = 30):
        """Initialize the trading strategy."""
        super().__init__(agent, interval)
        self.context.update({
            'last_trade_check': None,
            'position': None,
            'monitoring_tokens': ['ethereum', 'bitcoin'],
            'last_parent_id': None
        })
        
    def _format_price_data(self, price_data: Dict[str, Any]) -> str:
        """Format price data into a readable message."""
        result = []
        for token_id, data in price_data.items():
            price_usd = data.get('usd', 0)
            change_24h = data.get('usd_24h_change', 0)
            result.append(
                f"{token_id.title()}: ${price_usd:,.2f} "
                f"(24h change: {change_24h:+.2f}%)"
            )
        return "\\n".join(result)

    def generate_message(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate the next trading message based on market conditions."""
        ctx = context or self.get_context()
        token_list = ",".join(ctx.get('monitoring_tokens', ['ethereum', 'bitcoin']))
        
        message = (
            f"Let's analyze our trading position and current market conditions.\\n"
            f"1. Check our wallet balance\\n"
            f"2. Get current prices for {token_list} using get_token_price action\\n"
            f"3. Based on the price data and our current position, decide to:\\n"
            f"   a. Enter a new position\\n"
            f"   b. Exit current position\\n"
            f"   c. Hold current position\\n"
            f"Explain your reasoning and execute any necessary actions."
        )
        return message

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process the agent's response and track trading activity."""
        try:
            current_time = timezone.now()
            
            # Extract messages
            messages = response.get('messages', [])
            if not messages and isinstance(response.get('response'), dict):
                messages = response['response'].get('messages', [])
            
            # Process price data
            price_data = {}
            for msg in messages:
                if msg.get('type') == 'tool' and 'get_token_price' in str(msg.get('content', '')):
                    try:
                        content = json.loads(msg['content'])
                        if content.get('success') and content.get('data'):
                            price_data.update(content['data'])
                    except:
                        continue
            
            # Update context and response with price data
            if price_data:
                formatted_prices = self._format_price_data(price_data)
                market_data = {
                    'prices': price_data,
                    'timestamp': current_time.isoformat(),
                    'formatted': formatted_prices
                }
                self.update_context({'market_data': market_data})
                response['market_data'] = market_data
            
                # Track trade actions
                for msg in messages:
                    if msg.get('type') == 'tool' and 'trade' in str(msg.get('content', '')):
                        try:
                            trade_content = json.loads(msg['content'])
                            if trade_content.get('success'):
                                position = {
                                    'action': 'trade',
                                    'details': trade_content,
                                    'timestamp': current_time.isoformat()
                                }
                                self.update_context({
                                    'position': position,
                                    'last_trade_check': current_time
                                })
                        except:
                            continue

                # Process and store messages
                if messages:
                    last_message = messages[-1]
                    history = self.context.get('conversation_history', [])
                    history.append({
                        'message': last_message,
                        'message_id': self.context.get('last_message_id'),
                        'iteration': self.context['iteration_count'],
                        'market_data': market_data if price_data else None,
                        'position': position if 'position' in locals() else None
                    })
                    self.update_context({'conversation_history': history})
                    
                    # Update response with latest message only
                    response = {
                        'message': last_message,
                        'iteration': self.context['iteration_count'],
                        'conversation_id': self.context.get('current_conversation_id'),
                        'market_data': market_data if price_data else None,
                        'position_update': position if 'position' in locals() else None
                    }

            return response
            
        except Exception as e:
            logger.error(f"Error processing trading response: {str(e)}")
            return {
                "error": f"Failed to process trading response: {str(e)}",
                "original_response": response
            }
