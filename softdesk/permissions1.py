from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # Ne donnons l’accès qu’aux utilisateurs authentifiés
        return bool(request.user and request.user.is_authenticated)


class IsAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        # Ne donnons l’accès qu’aux utilisateurs authentifiés faisant partie du Staff
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
