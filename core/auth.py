"""
Authentication and authorization utilities
"""
from typing import Optional
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
import jwt

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication for the framework
    """
    def authenticate(self, request) -> Optional[tuple]:
        """
        Authenticate the request
        """
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            # Extract the token
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                return None

            # Decode and verify the token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256']
            )

            # Get the user
            user = User.objects.get(id=payload['user_id'])
            return (user, None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')


class AgentPermission(BasePermission):
    """
    Permission class for agent-related operations
    """
    def has_permission(self, request, view):
        """Check basic permission"""
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check object-level permission"""
        # Check if user owns the agent or has admin role
        return (
            obj.owner == request.user or
            request.user.is_staff or
            request.user.has_perm('agents.manage_all_agents')
        )


class WalletPermission(BasePermission):
    """
    Permission class for wallet operations
    """
    def has_permission(self, request, view):
        """Check basic permission"""
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check object-level permission"""
        # Allow access if user owns the agent that owns the wallet
        return (
            obj.agent.owner == request.user or
            request.user.is_staff or
            request.user.has_perm('wallet.manage_all_wallets')
        )


def generate_token(user: User) -> str:
    """
    Generate a JWT token for a user
    """
    payload = {
        'user_id': user.id,
        'email': user.email,
        'is_staff': user.is_staff
    }
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm='HS256'
    )


def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return its payload
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=['HS256']
        )
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')