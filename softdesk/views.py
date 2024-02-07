from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated


class CustomUserViewSetNew(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = [IsAuthenticated]

    def update(self, request, pk=None):
        instance = self.get_object()

        new_password = request.data['password']
        confirm_password = request.data['confirm_password']
        password = instance.password
        if new_password and confirm_password and new_password != '':
            if new_password != confirm_password:
                return Response({'message': ('Les mots de passe ne sont pas identiques')},
                                status=status.HTTP_400_BAD_REQUEST)
            elif password != new_password:
                instance.set_password(new_password)
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

        return Response()
