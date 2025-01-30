"""
Serializers for API management
"""
from rest_framework import serializers
from .models import APIKey, APIKeyUsage


class APIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for API keys
    """
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'permissions', 'is_active',
                 'last_used', 'expires_at', 'created_at']
        read_only_fields = ['key', 'last_used', 'created_at']
        extra_kwargs = {
            'key': {'write_only': True}  # Never send key in responses
        }


class APIKeyUsageSerializer(serializers.ModelSerializer):
    """
    Serializer for API key usage
    """
    class Meta:
        model = APIKeyUsage
        fields = ['endpoint', 'method', 'status_code', 'ip_address',
                 'response_time', 'error_message', 'created_at']