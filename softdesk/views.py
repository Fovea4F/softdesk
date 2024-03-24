from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models.deletion import ProtectedError

from .models import CustomUser, Project, Issue
from .serializers import CustomUserSerializer, CustomUserListSerializer
from . import project_serializers, issue_serializers
from .permissions import IsAuthor, IsContributor, IsAuthorOrAssignedContributor


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
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return []
        elif self.action == ['list', 'update', 'retrieve', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]

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
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
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


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = project_serializers.ProjectSerializer
    detail_serializer_class = project_serializers.ProjectDetailSerializer
    list_serializer_class = project_serializers.ProjectListSerializer
    update_serializer = project_serializers.ProjectUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # associate a specific Null Fields Serializer if not authenticated
        if not self.request.user.is_authenticated:
            return project_serializers.ProjectNullSerializer
        elif self.action == 'list':
            return project_serializers.ProjectListSerializer
        elif self.action == 'retrieve':
            return project_serializers.ProjectDetailSerializer
        elif self.action == 'update':
            return project_serializers.ProjectUpdateSerializer
        return project_serializers.ProjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            self.permission_classes = [IsContributor]
        elif self.action == 'retrieve':
            self.permission_classes = [IsContributor]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthor]
        elif self.action == 'update':
            self.permission_classes = [IsAuthor]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if request.user:
            data = request.data
            data['contributors'].append(request.user.pk)
            data['author'] = request.user.pk
        serializer = self.get_serializer(data=data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        self.check_permissions(request)
        # set connected user as author
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        if request.user.id is None:
            return Response({'error': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
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
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        project = get_object_or_404(Project, id=pk)
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        if project and user:
            contributors = project.contributors.all()
            # Verify if connected user is author or contributor
            if user not in contributors and user != project.author:
                return Response({'error': 'you are not project author or contributor'},
                                status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.get_serializer(project)
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

    @action(detail=False, methods=['post'], url_path='add')
    def contributor_add(self, request, project_id, pk=None):
        contributor_id = request.data.get('contributor_id')

        if contributor_id is None:
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

        if contributor_id is None:
            return Response({'error: no contributor id found in request'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                contributor = CustomUser.objects.get(pk=contributor_id)
            except CustomUser.DoesNotExist:
                return Response({f'error: {contributor_id} is not contributor'},
                                status=status.HTTP_404_NOT_FOUND)
            if not project.contributors.filter(id=contributor_id).exists():
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


class IssueViewSet(viewsets.ModelViewSet, RetrieveModelMixin, UpdateModelMixin):
    '''Manage project Issues.
        After creation, issue is owned by author,
        witch is initial creator and default designed contributor'''

    queryset = Issue.objects.all()
    serializer_class = issue_serializers.IssueSerializer
    permission_classes = [IsAuthor]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update']:
            perm = [IsAuthorOrAssignedContributor]
        elif self.action == 'destroy':
            perm = [IsAuthor]
        else:
            perm = []
        return [permission() for permission in perm]

    def get_serializer_class(self):
        if self.action == 'list':
            return issue_serializers.IssueListSerializer
        if self.action == 'create':
            return issue_serializers.IssueCreateSerializer
        return issue_serializers.IssueSerializer

    def create(self, request, *args, **kwargs):
        try:
            Project.objects.get(id=self.kwargs['project_pk'])
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        # give list of every assigned Issue for the connected user about the project
        project_id = kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_id)
        # verify if connected user is project author or in issues assigned_contributor
        if (request.user.pk != project.author.pk
                and not project.issues_list.filter(assigned_contributor=request.user.pk).exists()):
            return Response({'error': 'access not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        # Now, we know, generate queryset result of all issues about project_id where connected user is assigned user
        if request.user.pk == project.author.pk:
            queryset = project.issues_list.filter(author=request.user.pk)
        else:
            queryset = project.issues_list.filter(
                assigned_contributor=request.user.pk)
        # Serialize issues and bring response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        project_id = kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_id)
        # allow access to every user author or in contributors list
        if request.user.pk != project.author.pk and not project.contributors.filter(id=request.user.pk).exists():
            return Response({'error': 'access not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Issue.objects.get(pk=pk)

        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        issue = get_object_or_404(Issue, id=pk)
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        self.permission_classes = [IsAuthor, IsContributor]
        if issue and user:
            assigned_contributor = issue.assigned_contributor
            if user != assigned_contributor and user != issue.author:
                return Response({'error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.get_serializer(instance=issue, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
