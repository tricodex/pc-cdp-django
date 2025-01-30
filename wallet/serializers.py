"""
Serializers for wallet app
"""
from rest_framework import serializers
from .models import WalletConnection, WalletTransaction


class WalletConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet connections
    """
    class Meta:
        model = WalletConnection
        fields = ['id', 'address', 'chain_id', 'status', 'last_connected',
                 'metadata', 'created_at']
        read_only_fields = ['status', 'last_connected', 'created_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet transactions
    """
    class Meta:
        model = WalletTransaction
        fields = ['id', 'wallet', 'transaction_hash', 'transaction_type',
                 'status', 'data', 'error_message', 'gas_used', 'gas_price',
                 'block_number', 'created_at']
        read_only_fields = ['status', 'error_message', 'gas_used', 'gas_price',
                           'block_number', 'created_at']