from http import HTTPStatus
from rest_framework import viewsets, status, permissions
from rest_framework import generics
from rest_framework.response import Response
from .models import CustomUser
from . import serializers

from django.contrib.auth import get_user_model


'''class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class CustomUserCreationViewSet(viewsets.ModelViewSet):

    def create(self, request):
        serializer = serializers.CustomUserCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserListViewSet(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserListSerializer
    permission_classes = (permissions.IsAuthenticated, )
    # permission_classes = [permissions.AllowAny]


class CustomUserCreateViewSet1(viewsets.ModelViewSet):

    queryset = CustomUser.objects.none()
    serializer_class = serializers.CustomUserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):

        result = {
            'count': CustomUser.objects.count()
        }
        return Response(result, status=HTTPStatus.ACCEPTED)

    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomUserCreateSerializer(data=request.data)
        if not request.user.is_authenticated:
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet0(viewsets.ModelViewSet):

    list_serializer_class = serializers.CustomUserListSerializer
    detail_serializer_class = serializers.CustomUserDetailSerializer
    create_serializer_class = serializers.CustomUserCreateSerializer
    update_serializer_class = serializers.CustomUserUpdateSerializer
    delete_serializer_class = serializers.CustomUserDeleteSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CustomUser.objects.filter(active=True)

    def list(self, request, *args, **kwargs):
        return Response({"message": "L'affichage des utilisateurs n'est pas autorisé."}, status=403)

    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomUserSerializer(data=request.data)
        if not request.user.is_authenticated:
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_user_model().objects.filter(pk=self.request.user.id)


class CustomUserViewSet(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserListSerializer
    permission_classes_by_action = {'create': [], 'list': [permissions.IsAuthenticated]}

    def list(self, request, *args, **kwargs):
        if self.request.method == 'GET':
            serializer = serializers.CustomUserListSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response(request.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    def create(self, request, pk, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as error:
            errors = error.detail
            return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, pk)

    def update(self, request, pk):
        return super().update(request, pk)

    def partial_update(self, request, pk):
        return super().partial_update(request, pk)

    def delete(self, request, pk):
        return super().destroy(request, pk)


class TestViewSet(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()

    def list(self, request, *args, **kwargs):
        if request.method == 'GET':
            serializer = serializers.CustomUserListSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                # rajouter raise_exception permet de préciser l'erreur en cas de données non valides
                return Response(serializer.data)
            else:
                return Response({'details': 'invalid_data'})

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = serializers.CustomUserCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                # rajouter raise_exception permet de préciser l'erreur en cas de données non valides
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({'details': 'invalid_data'})
'''


class DetailApiView(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserListSerializer


class CreateApiView(generics.CreateAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserListSerializer


class CustomUserViewSetNew(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUser
