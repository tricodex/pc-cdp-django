"""
Views for wallet management
"""
from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import WalletConnection, WalletTransaction
from .serializers import WalletConnectionSerializer, WalletTransactionSerializer
from .services import WalletManager


class WalletConnectionView(views.APIView):
    """
    Handle wallet connections
    """
    def post(self, request):
        """Create connection challenge"""
        address = request.data.get('address')
        chain_id = request.data.get('chainId')
        
        if not address or not chain_id:
            raise ValidationError("Address and chainId are required")
            
        wallet_manager = WalletManager()
        challenge = wallet_manager.create_connection_challenge(address, chain_id)
        
        return Response(challenge)

    def put(self, request):
        """Verify connection signature"""
        address = request.data.get('address')
        signature = request.data.get('signature')
        
        if not address or not signature:
            raise ValidationError("Address and signature are required")
            
        wallet_manager = WalletManager()
        try:
            wallet_conn = wallet_manager.verify_connection(address, signature)
            serializer = WalletConnectionSerializer(wallet_conn)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WalletTransactionListView(generics.ListCreateAPIView):
    """
    List and create wallet transactions
    """
    serializer_class = WalletTransactionSerializer

    def get_queryset(self):
        """Filter transactions by wallet address"""
        address = self.kwargs.get('address')
        return WalletTransaction.objects.filter(wallet__address=address)

    def perform_create(self, serializer):
        """Create new transaction"""
        address = self.kwargs.get('address')
        try:
            wallet = WalletConnection.objects.get(address=address)
            serializer.save(wallet=wallet)
        except WalletConnection.DoesNotExist:
            raise ValidationError("Wallet connection not found")


class WalletTransactionDetailView(generics.RetrieveAPIView):
    """
    Retrieve transaction details
    """
    serializer_class = WalletTransactionSerializer
    lookup_field = 'transaction_hash'

    def get_queryset(self):
        """Filter transactions by wallet address"""
        address = self.kwargs.get('address')
        return WalletTransaction.objects.filter(wallet__address=address)