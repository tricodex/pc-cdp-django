"""
Signal handlers for the API app
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import APIKey, APIKeyUsage


@receiver(post_save, sender=APIKeyUsage)
def update_api_key_last_used(sender, instance, created, **kwargs):
    """
    Update the last_used timestamp of an API key when it's used
    """
    if created:
        instance.api_key.last_used = timezone.now()
        instance.api_key.save(update_fields=['last_used'])
