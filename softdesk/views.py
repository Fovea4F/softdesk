from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from .models import CustomUser, Project
from .serializers import CustomUserSerializer, CustomUserListSerializer
from .serializers import ProjectCreateSerializer, ProjectListSerializer, ProjectDetailSerializer, ProjectSerializer
from .permissions import IsOwnerOrAdmin, IsAuthenticated, IsAuthor, IsContributor


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


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
        instance = self.get_object()
        if instance != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        if instance is not None:
            instance.delete()
            return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'Message': ('Instance not found')}, status=status.HTTP_404_NOT_FOUND)


class ProjectViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    create_serializer_class = ProjectCreateSerializer
    serializer_list_class = ProjectListSerializer
    # Basic permission needed to permit Project creation
    permission_class = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        print('toto')
        return ProjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_class = [IsAuthenticated]
        if self.action == 'list':
            self.permission_class = [IsContributor]
        if self.action == 'destroy':
            self.permission_class = [IsAuthor]
        elif self.action == ['update', 'partial_update']:
            self.permission_class = [IsContributor]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # set connected user as author
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset().filter(contributors__in=[request.user])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        if instance is not None:
            instance.delete()
            return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'Message': ('Instance not found')}, status=status.HTTP_404_NOT_FOUND)
