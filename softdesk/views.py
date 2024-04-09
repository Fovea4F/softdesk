from django.shortcuts import get_object_or_404
from django.db.models.deletion import ProtectedError

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action

from . import customuser_serializers, project_serializers, issue_serializers, comment_serializers
from .models import CustomUser, Project, Issue, Comment
from .permissions import IsAuthor, IsAuthorOrAssignedContributor


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class CustomUserViewSet(viewsets.ModelViewSet):
    '''User management ViewSet :
        Only user can manage his (her) data
        Minimal authorized age over 15 '''

    queryset = CustomUser.objects.all()
    serializer_class = customuser_serializers.CustomUserSerializer
    serializer_list_class = customuser_serializers.CustomUserListSerializer
    permission_classes = [IsAuthenticated]

    '''def get_permissions(self):
        if self.action == 'create':  # permit only user creation without authentication
            return []
        elif self.action == ['list', 'update', 'retrieve', 'destroy']:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()'''

    def get_serializer_class(self):
        if self.action == 'list':
            return customuser_serializers.CustomUserListSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        '''Customer Creation'''
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        '''Give only active users list when authenticated'''
        queryset = CustomUser.objects.filter(is_active=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        '''Give User details to only owner'''
        instance = get_object_or_404(self.queryset, pk=pk)
        if instance != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(
            instance, context={'request': request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        ''' Permit partial informations updates to only Owner'''
        instance = self.get_object()
        if instance != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        '''Only Owner is authorized to destroy'''
        instance = self.get_object()
        if instance != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        if instance is not None:
            instance.delete()
            return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'Message': ('Instance not found')}, status=status.HTTP_404_NOT_FOUND)


class ProjectViewSet(viewsets.ModelViewSet):
    ''' Project Management accessible to connected user
        PROJECT_TYPES = "back-end",
                        "front-end",
                        "IOS",
                        "Android" '''

    queryset = Project.objects.all()
    serializer_class = project_serializers.ProjectSerializer
    detail_serializer_class = project_serializers.ProjectDetailSerializer
    list_serializer_class = project_serializers.ProjectListSerializer
    update_serializer = project_serializers.ProjectUpdateSerializer
    display_page_controls = True
    permission_classes = [IsAuthenticated]

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

    def create(self, request, *args, **kwargs):
        if request.user:
            data = request.data
            data['contributors'] = [(request.user.pk)]
            data['author'] = request.user.pk
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.check_permissions(request)
        # set connected user as author
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        if request.user.id is None:
            return Response({'error': 'not authorized'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(contributors__in=[request.user]).order_by('id')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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
                                status=status.HTTP_403_FORBIDDEN)
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
            return Response({'error': ('Data not found')}, status=status.HTTP_404_NOT_FOUND)


class ProjectContributorsViewSet(viewsets.ModelViewSet):
    '''Manage project contributors List.
        By design, Project Author is always in contributors list'''

    queryset = Project.objects.all()
    serializer_class = project_serializers.ProjectContributorSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='add')
    def contributor_add(self, request, project_id, pk=None):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if request.user != project.author:
            return Response({'error': 'you are not project author'}, status=status.HTTP_401_UNAUTHORIZED)
        contributor_id = request.data.get('contributor_id')
        if contributor_id is None:
            return Response({'error: no contributor id found in request'}, status=status.HTTP_400_BAD_REQUEST)
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

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if request.user != project.author:
            return Response({'error': 'you are not project author'}, status=status.HTTP_401_UNAUTHORIZED)
        contributor_id = request.data['contributor_id']
        try:
            contributor = CustomUser.objects.get(pk=contributor_id)
        except CustomUser.DoesNotExist:
            return Response({f'error: Contributor {contributor_id} does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not project.contributors.filter(id=contributor_id).exists():
            return Response(f'error: Contributor {contributor_id} not in project contributors list',
                            status=status.HTTP_400_BAD_REQUEST)
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs['project_pk']
        queryset = self.queryset.filter(project=pk)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return issue_serializers.IssueListSerializer
        if self.action == 'create':
            return issue_serializers.IssueCreateSerializer
        return issue_serializers.IssueSerializer

    def create(self, request, *args, **kwargs):
        '''Create a new issue, in accordance with connected user access rights on project'''
        project_pk = self.kwargs['project_pk']
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

        contributors = project.contributors.all()
        if self.request.user != project.author or self.request.user not in contributors:
            return Response({'error': 'user not authorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        ''' Give list of every assigned Issue for the connected user about the project, if rights on it'''

        project_pk = kwargs['project_pk']
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        # Serialize issues and bring response
        contributors = project.contributors.all()
        if self.request.user != project.author or self.request.user not in contributors:
            return Response({'error': 'user not authorized'}, status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset().filter(project__pk=project.pk).order_by('id')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        '''Give Issue Details '''
        project_pk = kwargs.get('project_pk')
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        contributors = project.contributors.all()
        if self.request.user != project.author or self.request.user not in contributors:
            return Response({'error': 'user not authorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            Issue.objects.get(pk=self.kwargs.get('pk'))
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not exist'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Issue.objects.get(pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        '''Possible to update partially Issue'''
        try:
            project = Project.objects.get(pk=kwargs.get('project_pk'))
            issues_list = project.issues_list.all()
            if Issue.objects.get(pk=self.kwargs.get('pk')) not in issues_list:
                return Response({'error': 'Issue not in Project List'}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            issue = Issue.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'error': 'Issue does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user != issue.author:
            return Response({'error': 'user unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance=issue, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        '''Suppress Issue : after request controls'''
        project_pk = kwargs.get('project_pk')
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        contributors = project.contributors.all()
        if self.request.user != project.author or self.request.user not in contributors:
            return Response({'error': 'user not authorized'}, status=status.HTTP_403_FORBIDDEN)
        issue = get_object_or_404(Issue, id=pk)
        issue.delete()
        return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    '''Comment are tickets written by any Project contributor'''

    queryset = Comment.objects.all()
    serializer_class = comment_serializers.CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return comment_serializers.CommentListSerializer
        if self.action == 'create':
            return comment_serializers.CommentSerializer
        return comment_serializers.CommentSerializer

    def create(self, request, issue_pk):
        try:
            issue = get_object_or_404(Issue, id=issue_pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if issue:
            # test if connected user is in project contributor list
            user = self.request.user
            if not issue.project.contributors.filter(id=user.id).exists():
                return Response({'error': 'Connected user unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                request.data['author'] = user.id
                request.data['issue_ref'] = issue.id
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(author=user, issue_ref=issue)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        # give list of every assigned Issue for the connected user about the project
        issue_id = kwargs['issue_pk']
        issue = get_object_or_404(Issue, pk=issue_id)
        # verify if connected user is project author or in issues assigned_contributor
        contributors = issue.project.contributors.all()
        if (request.user.pk != issue.project.author.pk) and (request.user not in contributors):
            return Response({'error': 'access not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            queryset = Comment.objects.filter(issue_ref=issue_id)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                return Response({'error': 'no data'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, issue_pk=None, *args, **kwargs):
        '''detail a comment, need to give UUID'''

        try:
            issue = get_object_or_404(Issue, pk=issue_pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if issue:
            # test if connected user is in project contributor list
            user = self.request.user
            if not issue.project.contributors.filter(id=user.id).exists():
                return Response({'error': 'Connected user unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                comment = get_object_or_404(Comment, pk=kwargs['pk'])
                # verify if connected user is project author or in issues assigned_contributor
                issue = comment.issue_ref
                queryset = Comment.objects.filter(uuid=comment.uuid)
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        '''update description field'''

        try:
            comment = Comment.objects.get(uuid=pk)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment does not exist'}, status=status.HTTP_404_NOT_FOUND)
        # Is connected_user allowed for this action ?
        if self.request.user != comment.author:
            return Response({'error': 'Connected user unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(instance=comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        '''Suppress a comment, need to give UUID'''
        comment = get_object_or_404(Comment, pk=pk)
        if comment:
            if (request.user != comment.author):  # Is connected user  the comment author ?
                return Response({'error': 'access not authorized.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                try:
                    comment.delete()
                    return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
                except ProtectedError as error:
                    error_message = f'{error} : not able to delete recorded data'
                    return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
