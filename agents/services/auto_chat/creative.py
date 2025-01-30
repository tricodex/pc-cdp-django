"""
Creative auto-chat strategy for evolving conversations.
"""
from typing import Dict, Any, Optional
from .base import AutoChatStrategy
import logging

logger = logging.getLogger(__name__)

class CreativeStrategy(AutoChatStrategy):
    """Creative strategy for evolving autonomous conversations."""
    
    def __init__(self, agent, interval: int = 30):
        """Initialize the creative strategy."""
        super().__init__(agent, interval)
        self.context.update({
            'conversation_history': [],
            'iteration_count': 0,
            'max_iterations': 5,
            'original_message': None,
            'completed_actions': set()
        })

    def generate_message(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate the next message based on conversation history and original request."""
        ctx = context or self.get_context()
        
        # Store original message on first iteration
        if self.context['iteration_count'] == 0:
            self.context['original_message'] = ctx.get('original_message')
            return self.context['original_message']
            
        self.context['iteration_count'] += 1
        history = ctx.get('conversation_history', [])
        completed = ctx.get('completed_actions', set())

        if not history:
            return self.context['original_message']

        # Analyze last response to track completed actions
        last_response = history[-1]
        last_content = last_response.get('content', '')
        
        # Track completed actions based on response content
        if 'get_token_price' in last_content:
            completed.add('price_check')
        if 'wallet' in last_content:
            completed.add('wallet_check')
        if 'search_web' in last_content:
            completed.add('web_search')
        if 'deploy_token' in last_content:
            completed.add('token_deployment')

        # Build follow-up prompt based on remaining actions
        remaining = []
        if 'price_check' not in completed:
            remaining.append("Get the latest price using get_token_price")
        if 'wallet_check' not in completed:
            remaining.append("Check wallet details and request funds if needed")
        if 'web_search' not in completed:
            remaining.append("Search for relevant information using search_web")
        if 'token_deployment' not in completed:
            remaining.append("Deploy a new token using deploy_token")

        if remaining:
            return (
                f"Following up on the previous step, let's continue with the next tasks:\n"
                f"{chr(10).join(f'- {task}' for task in remaining)}\n"
                f"\nPlease execute the next appropriate action and explain your progress."
            )
        
        self._stop = True  # All actions completed
        return "Great! All requested actions have been completed. Let me summarize what we've done."

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and store the agent's response."""
        try:
            if isinstance(response, dict):
                # Extract original message on first iteration
                if self.context['iteration_count'] == 0:
                    original_msg = response.get('original_message')
                    if original_msg:
                        self.context['original_message'] = original_msg

                # Process messages
                messages = response.get('messages', [])
                if not messages and isinstance(response.get('response'), dict):
                    messages = response['response'].get('messages', [])
                
                if messages:
                    # Store the last AI message
                    last_message = messages[-1]
                    history = self.context.get('conversation_history', [])
                    history.append(last_message)
                    self.update_context({'conversation_history': history})
                    response['conversation_history'] = history
                    
            return response
            
        except Exception as e:
            logger.error(f"Error processing creative response: {str(e)}")
            return {
                "error": f"Failed to process creative response: {str(e)}",
                "original_response": response
            }

    def should_continue(self) -> bool:
        """Determine if the conversation should continue."""
        return (
            not self._stop and 
            self.context['iteration_count'] < self.context['max_iterations']
        )
