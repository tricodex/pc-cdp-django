"""
Models for API management
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel

User = get_user_model()


class APIKey(TimeStampedModel):
    """
    Model for API keys
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True)
    permissions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def has_permission(self, permission: str) -> bool:
        """Check if key has specific permission"""
        return permission in self.permissions


class APIKeyUsage(TimeStampedModel):
    """
    Model for tracking API key usage
    """
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usage')
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    response_time = models.FloatField(help_text='Response time in seconds')
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.api_key.name} - {self.endpoint} ({self.status_code})"