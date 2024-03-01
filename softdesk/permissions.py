from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # Ne donne l’accès qu’aux utilisateurs authentifiés
        return bool(request.user and request.user.is_authenticated)


class IsAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        # Ne donne l’accès qu’aux utilisateurs authentifiés faisant partie du Staff
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Autorise l'utilisateur lui-même ou un administrateur à supprimer l'objet
        return obj == request.user or request.user.is_staff
