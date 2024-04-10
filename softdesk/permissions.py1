
from rest_framework import permissions
# from django.contrib.auth import get_user_model


'''class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # Ne donne l’accès qu’aux utilisateurs authentifiés
        return bool(request.user and request.user.is_authenticated)'''


class IsAdminAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ne donne l’accès qu’aux utilisateurs authentifiés faisant partie du Staff
        return (request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    # Autorise l'utilisateur lui-même ou un administrateur à supprimer l'objet
    def has_object_permission(self, request, view, obj):
        return obj.Author == request.user or request.user.is_staff


class IsAuthor(permissions.BasePermission):
    # True if request.user is Author of object
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    # True if object request.user is in contributors list

    def has_object_permission(self, request, view, obj):
        valid = obj.contributions.filter(user=request.user).exists()
        return valid


class IsAuthorOrAssignedContributor(permissions.BasePermission):
    def has_object_permissions(self, request, view, obj):
        return bool(request.user.is_authenticated and (request.user == obj.author or
                                                       request.user in obj.assigned_contributor.all())
                    )
