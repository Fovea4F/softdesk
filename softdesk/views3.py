from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers3 import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    '''def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Si la validation réussit, enregistrez l'utilisateur
            serializer.save()
            return Response({"message": "Utilisateur enregistré avec succès"}, status=status.HTTP_201_CREATED)
        else:
            # Si la validation échoue, renvoyez les erreurs
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

    '''def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valide(True)

        if self.validated_data['password'] and self.validated_data['confirm_password']:
                if self.validated_data['password'] != self.validated_data['confirm_password']:
                    return Response('error: passwords do not match !')confirm_password
                    = serializer.validated_data('confirm_password')
        if '''
