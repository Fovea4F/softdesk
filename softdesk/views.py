from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
# from rest_framework.settings import api_settings
from .models import CustomUser, Project
from .serializers import CustomUserSerializer, CustomUserListSerializer
from .serializers import ProjectSerializer, ProjectListSerializer, ProjectDetailSerializer, ProjectUpdateSerializer
# ProjectCreateSerializer,
from .permissions import IsOwnerOrAdmin, IsAuthenticated, IsAuthor, IsContributor

# from .permissions1 import is_user_authenticated


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
            return []
        elif self.action == 'list':
            self.permission_class = [IsAuthenticated]
        if self.action == 'destroy':
            self.permission_class = [IsAuthor]
        elif self.action == 'update':
            self.permission_class = [IsAuthor]
        elif self.action == 'retrieve':
            self.permission_class = [IsAuthor]
        return super().get_permissions()

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
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

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
    update_serializer_class = ProjectUpdateSerializer
    list_serializer_class = ProjectListSerializer
    permission_class = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        if self.action == 'update':
            return ProjectUpdateSerializer
        return ProjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_class = [IsAuthenticated]
        elif self.action == 'list':
            self.permission_class = [IsContributor]
        elif self.action == 'retrieve':
            self.permission_class = [IsContributor]
        elif self.action == 'destroy':
            self.permission_class = [IsAuthor]
        elif self.action == 'update':
            self.permission_class = [IsAuthor]

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

    def update(self, request, pk=None, *args, **kwargs):
        # A faire
        project = get_object_or_404(Project, id=pk)
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        if user != project.author:
            return Response({'error': 'you are not project author'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(project, data=request.data, partial=True)
        # serializer.validated_data.pop('contributors')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        project = get_object_or_404(Project, id=pk)
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        if project and user:
            contributors = project.contributors.all()
            if user not in contributors:
                return Response({'error': 'you are not project contributor'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.get_serializer(project)
            # serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        # A faire
        instance = self.get_object()
        if instance is not None:
            instance.delete()
            return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'Message': ('Instance not found')}, status=status.HTTP_404_NOT_FOUND)
