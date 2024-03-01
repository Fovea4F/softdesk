from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers2 import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission


'''class IsAuthenticatedForCreate(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
'''


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class CustomUserViewSet(viewsets.ModelViewSet, MultipleSerializerMixin):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def update(self, request, pk=None):
        instance = self.get_object()

        new_password = request.data['password']
        confirm_password = request.data['confirm_password']
        password = instance.password
        if new_password and confirm_password and new_password != '':
            if new_password != confirm_password:
                return Response({'message': ('Les mots de passe ne sont pas identiques')},
                                status=status.HTTP_400_BAD_REQUEST)
            elif password != new_password:
                instance.set_password(new_password)
        if request.data['birth_day']:
            instance.birth_day = request.data['birth_day']
        if 'can_be_contacted' not in request.data:
            instance.can_be_contacted = False
        else:
            instance.can_be_contacted = True
        if 'can_be_shared' not in request.data:
            instance.can_be_shared = False
        else:
            instance.can_be_shared = True
        instance.save()

        return Response()

    def create(self, request):

        new_password = request.data['password']
        confirm_password = request.data['confirm_password']
        if new_password and confirm_password and new_password != '':
            if new_password != confirm_password:
                return Response({'message': ('Les mots de passe ne sont pas identiques')},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response()
