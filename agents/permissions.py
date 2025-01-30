"""
Permissions for agents app
"""
from rest_framework import permissions


class AgentPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an agent to edit it.
    """
    def has_permission(self, request, view):
        # Allow all authenticated users to list and create
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner.
        return obj.owner == request.user or request.user.is_staff