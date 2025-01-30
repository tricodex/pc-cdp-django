"""
Admin configuration for agents app
"""
from django.contrib import admin
from .models import Agent, AgentAction, AgentWallet, TokenPrice, PriceCache


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'owner', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AgentAction)
class AgentActionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'action_type', 'status', 'created_at')
    list_filter = ('action_type', 'status')
    search_fields = ('agent__name', 'action_type')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AgentWallet)
class AgentWalletAdmin(admin.ModelAdmin):
    list_display = ('agent', 'wallet_id', 'network_id', 'address', 'is_active')
    list_filter = ('network_id', 'is_active')
    search_fields = ('agent__name', 'wallet_id', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TokenPrice)
class TokenPriceAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'price_usd', 'price_eth', 'timestamp', 'created_at')
    list_filter = ('token_id', 'timestamp')
    search_fields = ('token_id',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-timestamp',)


@admin.register(PriceCache)
class PriceCacheAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'created_at', 'expires_at')
    list_filter = ('token_id',)
    search_fields = ('token_id',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
