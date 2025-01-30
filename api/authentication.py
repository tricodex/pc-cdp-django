"""
Custom authentication for API keys
"""
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from django.conf import settings

from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using API keys
    """
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None

        try:
            key = APIKey.objects.get(key=api_key, is_active=True)
            
            # Update last used timestamp
            key.last_used = timezone.now()
            key.save(update_fields=['last_used'])
            
            return (key.user, key)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        except Exception as e:
            raise AuthenticationFailed(str(e))