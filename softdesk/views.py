from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
# from django.core.exceptions import ProtectedError
from django.db.models.deletion import ProtectedError

from .models import CustomUser, Project
from .serializers import CustomUserSerializer, CustomUserListSerializer
# from .serializers import ProjectSerializer, ProjectListSerializer, ProjectDetailSerializer
from . import project_serializers
from .permissions import IsAuthenticated, IsAuthor, IsContributor


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
    serializer_class = project_serializers.ProjectSerializer
    detail_serializer_class = project_serializers.ProjectDetailSerializer
    update_serializer_class = project_serializers.ProjectUpdateSerializer
    list_serializer_class = project_serializers.ProjectListSerializer
    permission_class = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return project_serializers.ProjectListSerializer
        if self.action == 'retrieve':
            return project_serializers.ProjectDetailSerializer
        if self.action == 'update':
            return project_serializers.ProjectUpdateSerializer
        return project_serializers.ProjectSerializer

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
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # set connected user as author
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset().filter(contributors__in=[request.user])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        project = get_object_or_404(Project, id=pk)
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        if user != project.author:
            return Response({'error': 'you are not project author'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(project, data=request.data, partial=True)
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

    def destroy(self, request, pk=None, *args, **kwargs):
        project = get_object_or_404(Project, id=pk)
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        if user != project.author:
            return Response({'error': 'you are not project author'}, status=status.HTTP_401_UNAUTHORIZED)
        if project is not None:
            try:
                project.delete()
                return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
            except ProtectedError as error:
                error_message = f'not able to delete recorded data : {error}'
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Message': ('Data not found')}, status=status.HTTP_404_NOT_FOUND)


class ProjectContributorsViewSet(viewsets.ModelViewSet):
    '''Manage project contributors List.
        By design, Project Author is always in contributors list'''

    queryset = Project.objects.all()
    serializer_class = project_serializers.ProjectContributorSerializer
    permission_classes = [IsAuthor]

    '''def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_class = [IsAuthor]
        if self.action == 'update':
            self.permission_class = [IsAuthor]
        return super().get_permissions()'''

    def check_project_exist(project_id):
        try:
            project = Project.objects.get(pk=project_id)
        except ObjectDoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return project

    @action(detail=False, methods=['post'], url_path='add')
    def contributor_add(self, request, project_id, pk=None):
        contributor_id = request.data.get('contributor_id')

        if contributor_id == None:
            return Response({'error: no contributor id found in request'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                contributor = CustomUser.objects.get(pk=contributor_id)
            except CustomUser.DoesNotExist:
                return Response({f'error: Contributor {contributor_id} does not exist'},
                                status=status.HTTP_404_NOT_FOUND)

            project.contributors.add(contributor)
            project.save()

            serializer = self.get_serializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='delete')
    def contributor_delete(self, request, project_id, pk=None):
        contributor_id = request.data.get('contributor_id')

        if contributor_id == None:
            return Response({'error: no contributor id found in request'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                contributor = CustomUser.objects.get(pk=contributor_id)
            except CustomUser.DoesNotExist:
                return Response({f'error: Contributor {contributor_id} does not exist'},
                                status=status.HTTP_404_NOT_FOUND)
            if not project.contributors.filter(id=contributor_id).exists():
                # if contributor_id not in project.contributors.all().values_list('id', flat=True):
                return Response(f'error: Contributor {contributor_id} not in project list',
                                status=status.HTTP_404_NOT_FOUND)
            elif int(contributor_id) == project.author_id:
                return Response({'error: You cannot suppress project author from contributors list'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                project.contributors.remove(contributor)
                project.save()

            serializer = self.get_serializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
