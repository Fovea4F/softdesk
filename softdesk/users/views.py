from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


from ..permissions import IsOwnerOrAdmin, IsAuthenticated, IsAuthor, IsContributor
from ..serializers import CustomUserSerializer, CustomUserListSerializer
from ..models import CustomUser


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    serializer_list_class = CustomUserListSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            # Autorise uniquement les requêtes POST sans authentification
            return []
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomUserListSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(status=status.HTTP_202_ACCEPTED)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        if instance != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(
            instance, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        pass
