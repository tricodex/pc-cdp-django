"""
Admin configuration for API app
"""
from django.contrib import admin
from .models import APIKey, APIKeyUsage


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'last_used', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__email')
    readonly_fields = ('key', 'last_used')


@admin.register(APIKeyUsage)
class APIKeyUsageAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'endpoint', 'method', 'status_code', 'created_at')
    list_filter = ('method', 'status_code')
    search_fields = ('api_key__name', 'endpoint')