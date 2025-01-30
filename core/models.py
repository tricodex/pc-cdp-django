"""
Core models for the multi-agent framework.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Status(models.TextChoices):
    """
    Common status choices for various models
    """
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    PENDING = 'pending', 'Pending'
    ERROR = 'error', 'Error'
    COMPLETED = 'completed', 'Completed'


class BaseConfig(TimeStampedModel):
    """
    Base configuration model for storing key-value pairs
    """
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.key}: {self.value}"