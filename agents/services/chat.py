"""
Chat-related services for agents.
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, Generator, Union
import uuid
from django.db import transaction
from core.exceptions import AgentConfigurationError
from cdp_langchain.utils import CdpAgentkitWrapper
from langchain_core.messages import (
    HumanMessage, 
    AIMessage,
    ToolMessage,
    BaseMessage
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from ..models import AgentAction, ChatMessage
from .base import BaseAgentService
from .auto_chat import AVAILABLE_STRATEGIES
from ..toolkits import CustomAgentToolkit
import logging

logger = logging.getLogger(__name__)

def serialize_langchain_message(msg: Union[Dict, BaseMessage, Any]) -> Dict[str, Any]:
    """Helper function to serialize LangChain messages"""
    if isinstance(msg, (HumanMessage, AIMessage, ToolMessage)):
        message_type = "human"
        if isinstance(msg, AIMessage):
            message_type = "ai"
        elif isinstance(msg, ToolMessage):
            message_type = "tool"
        
        serialized = {
            "type": message_type,
            "content": msg.content
        }
        
        # Include additional fields for tool messages
        if isinstance(msg, ToolMessage) and hasattr(msg, 'tool_call_id'):
            serialized['tool_call_id'] = msg.tool_call_id
            
        return serialized
    
    elif isinstance(msg, dict):
        if "messages" in msg:
            return {
                "messages": [
                    serialize_langchain_message(m) for m in msg["messages"]
                    if m is not None  # Skip None messages
                ]
            }
        else:
            return {
                k: serialize_langchain_message(v) 
                for k, v in msg.items() 
                if v is not None  # Skip None values
            }
    
    elif isinstance(msg, list):
        return [
            serialize_langchain_message(m) for m in msg 
            if m is not None  # Skip None values
        ]
    
    elif msg is None:
        return None
        
    else:
        # For any other type, try to convert to string if not serializable
        try:
            # Try to serialize as-is first
            json.dumps(msg)
            return msg
        except (TypeError, ValueError):
            # If not serializable, convert to string
            return str(msg)


class ChatService(BaseAgentService):
    """Service for managing agent chat functionality."""
    
    def __init__(self, agent_model, agentkit: Optional[CdpAgentkitWrapper] = None):
        """Initialize chat service"""
        super().__init__(agent_model, agentkit)
        self._toolkit = None
        self._llm = None
        self._agent_executor = None
        self._config = None
        self._strategy = None

    def _ensure_agent_initialized(self):
        """Ensure agent components are initialized"""
        if self._agent_executor is None:
            try:
                # Initialize LLM if needed
                if self._llm is None:
                    self._llm = ChatOpenAI(model="gpt-4o-mini")

                # Initialize toolkit if needed
                if self._toolkit is None:
                    if not self.agentkit:
                        raise AgentConfigurationError("CDP Agentkit wrapper not initialized")
                    self._toolkit = CustomAgentToolkit.from_cdp_agentkit_wrapper(self.agentkit)

                # Initialize memory and config
                memory = MemorySaver()
                self._config = {"configurable": {"thread_id": f"Agent-{self.agent.id}-Chat"}}

                # Create ReAct agent
                agent_tuple = create_react_agent(
                    self._llm,
                    tools=self._toolkit.get_tools(),
                    checkpointer=memory,
                    state_modifier=(
                        "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
                        "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
                        "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
                        "details and request funds from the user. Before executing your first action, get the wallet details "
                        "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
                        "again later. If someone asks you to do something you can't do with your currently available tools, "
                        "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
                        "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
                        "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
                    ),
                )
                
                # Handle both tuple and direct return cases
                self._agent_executor = agent_tuple[0] if isinstance(agent_tuple, tuple) else agent_tuple

            except Exception as e:
                self._log_error("Failed to initialize agent components", e)
                raise AgentConfigurationError(f"Failed to initialize agent components: {str(e)}")

    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format the response from the agent"""
        try:
            # Try to find AI message content in different response formats
            if isinstance(response, dict):
                if 'output' in response:
                    return {"response": response['output']}
                elif 'messages' in response:
                    ai_messages = [
                        msg for msg in response['messages'] 
                        if isinstance(msg, dict) and msg.get('type') == 'ai'
                    ]
                    if ai_messages:
                        return {"response": ai_messages[-1].get('content', '')}
            
            # If can't find specific AI message, return serialized full response
            return {"response": serialize_langchain_message(response)}
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return {"error": "Failed to process response"}

    @transaction.atomic
    def chat_sync(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a chat message synchronously"""
        self._ensure_agent_initialized()
        
        # Create action record
        action = AgentAction.objects.create(
            agent=self.agent,
            action_type="chat_message",
            parameters={"message": message},
            status="pending"
        )
        
        # Create human message record
        human_msg = ChatMessage.objects.create(
            agent=self.agent,
            message_type=ChatMessage.MessageType.HUMAN,
            content=message,
            conversation_id=conversation_id or uuid.uuid4()  # Create new conversation if none provided
        )

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the agent
                result = loop.run_until_complete(
                    self._agent_executor.ainvoke(
                        {"messages": [HumanMessage(content=message)]},
                        self._config
                    )
                )
                
                # Serialize and process the result
                serialized_result = self._process_response(result)
                
                # Create AI message record
                ChatMessage.objects.create(
                    agent=self.agent,
                    message_type=ChatMessage.MessageType.AI,
                    content=serialized_result.get('response', ''),
                    metadata=serialized_result,
                    parent_message=human_msg,
                    conversation_id=human_msg.conversation_id
                )
                
                # Update action record with success
                action.status = "completed"
                action.result = serialized_result
                action.save()
                
                return serialized_result
                
            finally:
                loop.close()
                
        except Exception as e:
            # Update action record with error
            action.status = "error"
            action.error_message = str(e)
            action.save()
            
            self._log_error("Chat failed", e)
            raise AgentConfigurationError(f"Chat processing error: {str(e)}")

    @transaction.atomic
    def stream_chat_sync(self, message: str, conversation_id: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        """Stream chat responses synchronously"""
        self._ensure_agent_initialized()

        # Create action record
        action = AgentAction.objects.create(
            agent=self.agent,
            action_type="chat_message",
            parameters={"message": message},
            status="pending",
            result={"responses": []}
        )
        
        # Create human message record
        human_msg = ChatMessage.objects.create(
            agent=self.agent,
            message_type=ChatMessage.MessageType.HUMAN,
            content=message,
            conversation_id=conversation_id or uuid.uuid4()
        )

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Create async generator
                async def generate():
                    async for chunk in self._agent_executor.stream(
                        {"messages": [HumanMessage(content=message)]},
                        self._config
                    ):
                        # Serialize and process the chunk
                        processed_chunk = self._process_response(chunk)
                        if "error" not in processed_chunk:
                            yield processed_chunk
                
                # Run the generator in the loop
                gen = generate()
                while True:
                    try:
                        chunk = loop.run_until_complete(gen.__anext__())
                        # Update action record
                        action.result["responses"].append(chunk)
                        action.save()
                        yield chunk
                    except StopAsyncIteration:
                        break

                # Mark action as completed
                action.status = "completed"
                action.save()
                
            finally:
                loop.close()
                
        except Exception as e:
            # Update action record with error
            action.status = "error"
            action.error_message = str(e)
            action.save()
            
            self._log_error("Chat stream failed", e)
            yield {"error": str(e)}

    def stream_auto_chat(self, message: str, interval: int = 10, strategy_name: str = None, conversation_id: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        """Stream autonomous chat responses synchronously with interval"""
        self._ensure_agent_initialized()

        try:
            # Initialize strategy if specified
            if strategy_name and strategy_name in AVAILABLE_STRATEGIES:
                self._strategy = AVAILABLE_STRATEGIES[strategy_name](self.agent, interval)
            elif not self._strategy:
                self._strategy = AVAILABLE_STRATEGIES['default'](self.agent, interval)
            
            # Generate new conversation ID if not provided
            conv_id = conversation_id or uuid.uuid4()

            # Initialize strategy context
            self._strategy.update_context({
                'original_message': message,
                'iteration_count': 0,
                'current_conversation_id': conv_id,
                'last_message_id': None
            })
            
            # Create initial human message
            human_msg = ChatMessage.objects.create(
                agent=self.agent,
                message_type=ChatMessage.MessageType.HUMAN,
                content=message,
                conversation_id=conv_id,
                metadata={'auto_chat': True, 'strategy': strategy_name}
            )
            
            action = AgentAction.objects.create(
                agent=self.agent,
                action_type="auto_chat",
                parameters={
                    "message": message, 
                    "interval": interval,
                    "strategy": strategy_name
                },
                status="pending",
                result={"responses": []}
            )

            while True:
                try:
                    # Use the strategy's generate_message with context
                    current_message = message if self._strategy.context['iteration_count'] == 0 else self._strategy.generate_message()
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        result = loop.run_until_complete(
                            self._agent_executor.ainvoke(
                                {"messages": [HumanMessage(content=current_message)]},
                                self._config
                            )
                        )
                        
                        # Process and yield the result
                        processed_result = self._process_response(result)
                        
                        # Process through strategy if available
                        if self._strategy:
                            processed_result = self._strategy.process_response(processed_result)
                            
                        # Create AI message for auto-chat response
                        ai_msg = ChatMessage.objects.create(
                            agent=self.agent,
                            message_type=ChatMessage.MessageType.AI,
                            content=processed_result.get('response', ''),
                            metadata={
                                **processed_result,
                                'auto_chat': True,
                                'strategy': strategy_name,
                                'iteration': self._strategy.context.get('iteration_count', 0)
                            },
                            parent_message=ChatMessage.objects.get(id=self._strategy.context['last_message_id']) if self._strategy.context.get('last_message_id') else human_msg,
                            conversation_id=conv_id
                        )
                        
                        # Update last message id in context
                        self._strategy.update_context({'last_message_id': ai_msg.id})
                        
                        # Only yield the latest message, not the entire history
                        response_data = {
                            'response': {
                                'type': 'ai',
                                'content': processed_result.get('response', ''),
                                'metadata': {
                                    'auto_chat': True,
                                    'strategy': strategy_name,
                                    'iteration': self._strategy.context.get('iteration_count', 0)
                                },
                                'conversation_id': str(conv_id)
                            }
                        }
                        
                        # Add to action history
                        action.result["responses"].append(response_data)
                        action.save()
                        
                        # Yield only the latest response
                        yield response_data
                        
                        # Check if strategy wants to continue
                        if self._strategy and not self._strategy.should_continue():
                            break
                        
                    finally:
                        loop.close()

                    # Wait for the specified interval
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Auto-chat iteration failed: {str(e)}")
                    yield {"error": f"Auto-chat iteration failed: {str(e)}"}
                    break

            # Mark action as completed after breaking from the loop
            action.status = "completed"
            action.save()

        except Exception as e:
            action.status = "error"
            action.error_message = str(e)
            action.save()
            
            self._log_error("Auto-chat failed", e)
            yield {"error": str(e)}
