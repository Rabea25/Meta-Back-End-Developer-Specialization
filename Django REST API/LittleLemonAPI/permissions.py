from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Custom permission to allow only users in the 'Manager' group.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists() or request.user.is_superuser