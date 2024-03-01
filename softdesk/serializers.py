from rest_framework import serializers
from datetime import date
from rest_framework.response import Response

from .models import CustomUser, Project


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    can_be_contacted = serializers.BooleanField(default=False)
    can_be_shared = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'birth_day', 'can_be_contacted',
                  'can_be_shared', 'password', 'confirm_password']

    def validate(self, data):
        '''Validate if customer Age at creation is more than 15'''
        birth = data['birth_day']
        today = date.today()
        authorized_age = 15

        accept_registration = False
        if today.year - birth.year >= authorized_age:
            if today.year - birth.year == authorized_age:
                if today.month >= birth.month:
                    if today.month == birth.month:
                        if today.day >= birth.day:
                            accept_registration = True
                else:
                    accept_registration = True
            else:
                accept_registration = True
        if not accept_registration:
            raise serializers.ValidationError(
                'error: age less than required, you are not allowed to register')
        confirm_password = data['confirm_password']
        if data['password'] and confirm_password:
            if data['password'] != confirm_password:
                raise serializers.ValidationError(
                    'error: passwords do not match !')
            return data

    def create(self):
        if self.is_valid(raise_exception=True):
            # Supprimer champ de confirmation du mot de passe avant sauvegarde
            self.validated_data.pop('confirm_password')
            self.validated_data['username'] = self.validated_data['email']
            return CustomUser.objects.create_user(**self.validated_data)

    '''def update(self, instance, validated_data):
        if validated_data['password'] == instance.password:
            raise serializers.ValidationError('error: Password not changed.')
        instance.password = validated_data.get('password', instance.password)
        instance.birth_day = validated_data.get(
            'birth_day', instance.birth_day)
        instance.save()
        return instance'''


class ProjectListSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author']


class ProjectDetailSerializer(serializers.ModelSerializer):
    '''Serializer for Projects Detail'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'contributors', 'project_type', 'description', 'created_date']

        def update(self, request, *args, **kwargs):
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)


class ProjectCreateSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entity    creation'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'contributors', 'project_type', 'description', 'created_date']

        '''def create_(self, validated_data):
            # Set the initial contributor as the author
            validated_data['contributors'] = validated_data['author']

            return super().create(validated_data)'''

        def create(self, validated_data):
            # Get the author from the validated data
            author = validated_data['author']

            # Create the instance without saving it yet
            instance = Project.objects.create(**validated_data)

            # If author is provided, add it to the contributors
            if author:
                instance.contributors.add(author)

            return instance
