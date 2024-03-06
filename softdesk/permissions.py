from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # Ne donne l’accès qu’aux utilisateurs authentifiés
        return bool(request.user and request.user.is_authenticated)


class IsAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        # Ne donne l’accès qu’aux utilisateurs authentifiés faisant partie du Staff
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    # Autorise l'utilisateur lui-même ou un administrateur à supprimer l'objet
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsAuthor(IsAuthenticated):
    # True if request.user is Author of object
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(IsAuthenticated):
    # True if object request.user is in contributors list
    def has_object_permission(self, request, view, obj):
        return obj.contributions.filter(user=request.user).exists()
