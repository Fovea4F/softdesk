from rest_framework import viewsets, status
from rest_framework.decorators import action
# from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from .models import CustomUser, Project
from .serializers import CustomUserSerializer, ProjectListSerializer, ProjectDetailSerializer, ProjectCreateSerializer
from .permissions import IsOwnerOrAdmin


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsOwnerOrAdmin]

    '''def get_permissions(self):
        if self.action == 'create':
            # Autorise uniquement les requêtes POST sans authentification
            return []
        return [permissions.IsAuthenticated()]
    '''

    def update(self, request, pk=None):
        instance = self.get_object()

        new_password = request.data['password']
        confirm_password = request.data['confirm_password']
        password = instance.password
        if new_password and confirm_password:
            if new_password != confirm_password:
                return Response({'message': ('Password do not match')},
                                status=status.HTTP_400_BAD_REQUEST)
            elif password != new_password:
                instance.set_password(new_password)
            else:
                return Response({'message': ('You cannot use the old password for renewal')},
                                status=status.HTTP_400_BAD_REQUEST)
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

        return Response({'message': ('Changes validated')}, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        if instance is not None:
            self.perform_destroy(instance)
            return Response({'message': ('Destroy action ok')}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'Message': ('Instance not found')}, status=status.HTTP_404_NOT_FOUND)


# @permission_classes([IsOwnerOrAdmin])
class ProjectListViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    create_serializer_class = ProjectCreateSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        else:
            return ProjectListSerializer

    '''def list(self, request, *args, **kwargs):
        # Add 'POST' to the list of allowed methods for the list page
        self.http_method_names.append('post')
        return super().list(request, *args, **kwargs)'''

    def create(self, request):
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        project.delete()
        return Response({'message': ('Item deleted')}, status=status.HTTP_204_NO_CONTENT)


class ProjectCreateViewSet(viewsets.ViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectCreateSerializer

    '''def create(self, request):
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)'''

    def perform_create(self, serializer):
        contributors_data = self.request.data.get('author', [])
        instance = serializer.save()
        instance.contributors.set(contributors_data)  # Set the contributors for the instance
        instance.save()
