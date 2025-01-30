"""
Middleware for API request handling
"""
import time
from typing import Callable
from django.http import HttpRequest, HttpResponse
from .models import APIKeyUsage


class APIMetricsMiddleware:
    """
    Middleware to track API metrics
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Start timer
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate response time
        response_time = time.time() - start_time

        # Update usage metrics if this was an API key request
        if hasattr(request, 'auth') and request.auth:
            try:
                usage = APIKeyUsage.objects.filter(
                    api_key=request.auth,
                    endpoint=request.path,
                    method=request.method
                ).latest('created_at')
                
                usage.status_code = response.status_code
                usage.response_time = response_time
                if response.status_code >= 400:
                    usage.error_message = getattr(response, 'data', {}).get('error', '')
                usage.save()
            except APIKeyUsage.DoesNotExist:
                pass

        return response


class RateLimitMiddleware:
    """
    Middleware for custom rate limiting
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Implement custom rate limiting here if needed
        return self.get_response(request)