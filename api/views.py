"""
Views for API management
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import APIKey, APIKeyUsage
from .serializers import APIKeySerializer, APIKeyUsageSerializer
from core.auth import JWTAuthentication
from core.throttling import DocumentationSearchThrottle


class APIKeyListView(generics.ListCreateAPIView):
    """
    List and create API keys
    """
    serializer_class = APIKeySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [DocumentationSearchThrottle]

    def get_queryset(self):
        """Filter keys by user"""
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create new API key"""
        serializer.save(user=self.request.user)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete API keys
    """
    serializer_class = APIKeySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [DocumentationSearchThrottle]

    def get_queryset(self):
        """Filter keys by user"""
        return APIKey.objects.filter(user=self.request.user)


class APIKeyUsageView(views.APIView):
    """
    View API key usage metrics
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [DocumentationSearchThrottle]

    def get(self, request, pk):
        """Get usage metrics for an API key"""
        try:
            api_key = APIKey.objects.get(id=pk, user=request.user)
        except APIKey.DoesNotExist:
            return Response(
                {"error": "API key not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get usage statistics
        usage = APIKeyUsage.objects.filter(api_key=api_key)
        total_requests = usage.count()
        successful_requests = usage.filter(status_code__lt=400).count()
        error_requests = usage.filter(status_code__gte=400).count()
        avg_response_time = usage.values_list('response_time', flat=True).aggregate('avg')

        # Get recent usage
        recent_usage = usage.order_by('-created_at')[:10]
        serializer = APIKeyUsageSerializer(recent_usage, many=True)

        return Response({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'error_requests': error_requests,
            'average_response_time': avg_response_time,
            'recent_usage': serializer.data,
            'last_used': api_key.last_used,
            'created_at': api_key.created_at
        })