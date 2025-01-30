"""
Chat and communication views
"""
from rest_framework import views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

from core.auth import AgentPermission
from core.throttling import AgentActionThrottle
from ..models import Agent
from ..services import DeFiAgentManager

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class AgentChatView(views.APIView):
    """Chat with an agent"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]
    
    def post(self, request, pk):
        """Process chat message"""
        try:
            agent = get_object_or_404(Agent, pk=pk)
            self.check_object_permissions(request, agent)
            
            message = request.data.get('message')
            conversation_id = request.data.get('conversation_id')
            
            if not message:
                return Response(
                    {"error": "message is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            manager = DeFiAgentManager(agent)
            
            # Check if streaming is requested
            stream = request.query_params.get('stream', 'false').lower() == 'true'
            
            if stream:
                def stream_generator():
                    try:
                        for chunk in manager.stream_chat_sync(message, conversation_id=conversation_id):
                            yield f"data: {json.dumps(chunk)}\n\n"
                    except Exception as e:
                        logger.error(f"Stream generation error: {str(e)}")
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

                response = StreamingHttpResponse(
                    stream_generator(),
                    content_type='text/event-stream'
                )
                # Set headers for streaming response
                response["X-Accel-Buffering"] = "no"
                response["Cache-Control"] = "no-cache"
                return response
                
            else:
                try:
                    result = manager.chat_sync(message, conversation_id=conversation_id)
                    return Response(result)
                except Exception as e:
                    logger.error(f"Chat processing error: {str(e)}")
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
        except Exception as e:
            logger.error(f"Chat failed for agent {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class AgentAutoChatView(views.APIView):
    """Run agent in autonomous chat mode"""
    permission_classes = [AgentPermission]
    throttle_classes = [AgentActionThrottle]
    
    def post(self, request, pk):
        """Start autonomous chat mode"""
        try:
            agent = get_object_or_404(Agent, pk=pk)
            self.check_object_permissions(request, agent)
            
            interval = int(request.data.get('interval', 10))
            conversation_id = request.data.get('conversation_id')
            message = request.data.get('message', (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            ))
            
            manager = DeFiAgentManager(agent)
            
            def stream_generator():
                try:
                    for chunk in manager.stream_auto_chat(
                        message,
                        interval=interval,
                        conversation_id=conversation_id
                    ):
                        yield f"data: {json.dumps(chunk)}\n\n"
                except Exception as e:
                    logger.error(f"Auto-chat stream error: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            response = StreamingHttpResponse(
                stream_generator(),
                content_type='text/event-stream'
            )
            response["X-Accel-Buffering"] = "no"
            response["Cache-Control"] = "no-cache"
            return response
                
        except Exception as e:
            logger.error(f"Auto-chat failed for agent {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
