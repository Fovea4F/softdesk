from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
# from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from .models import CustomUser
from . import serializers1
from rest_framework.permissions import IsAuthenticated


class CustomUserViewSet(viewsets.ModelViewSet):

    serializer_class = serializers1.CustomUserListSerializer
    detail_serializer_class = serializers1.CustomUserDetailSerializer
    # partial_update_serializer_class = CustomUserUpdateSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def list(self, request: Request):
        queryset = CustomUser.objects.filter(is_active=True)
        serializer = serializers1.CustomUserListSerializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Create a new User"""

        serializer = serializers1.CustomUserCreateSerializer(data=request.data)

        if serializer.is_valid():
            message = 'User created'
            return Response({'message': message})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

    def retrieve(self, request: Request, pk=None):
        """Return a User details"""

        user = get_object_or_404(CustomUser, pk=pk)

        serializer = serializers1.CustomUserDetailSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Ready to modify user data1l"""

        return Response({'http method': 'PUT'})

    def partial_update(self, request, pk=None):
        """Ready to modify some user data1l"""

        return Response({'http method': 'PATCH'})

    def destroy(self, request, pk=None):
        """Ready to Remove user"""

        return Response({'http method': 'DELETE'})
