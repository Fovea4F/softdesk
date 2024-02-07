from rest_framework import serializers
# from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomUser


class CustomUserCreationSerializer0(serializers.ModelSerializer):
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'password', 'confirm_password', 'first_name', 'last_name', 'email', 'birth_day',
                  'can_be_shared', 'can_be_contacted'
                  )
        pass_kargs = {'password': {'write_only': True}, 'confirm_password': {'write_only': True}}

    def password_validate(self):
        password = self.data.get('password')
        confirm_password = self.data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("The 2 passwords are not identical")

        try:
            validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError(error.messages)

        return self.data

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            email=validated_data['email'],
            last_name=validated_data['last_name'],
            birth_day=validated_data['birth_day'],
            can_be_shared=validated_data['can_be_shared'],
            can_be_contacted=validated_data['can_be_contacted'],
        )
        return user


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'birth_day')


class UserConnexionSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        user = get_user_model()
        if user and user.is_active:
            return UserConnexionSerializer
        raise serializers.ValidationError("Bad identification informations")


class ListUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email',)


class CustomUserCreateSerializer1(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'birth_day',
                  'can_be_contacted', 'can_be_shared')


class CustomUserCreateSerializer2(serializers.ModelSerializer):
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'confirm_password', 'first_name', 'last_name', 'email', 'birth_day',
                  'can_be_shared', 'can_be_contacted'
                  )
        extra_kargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = CustomUser.objects.create_user(**validated_data)
            return user


class CustomUserCreateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'confirm_password', 'birth_day', 'can_be_shared', 'can_be_contacted')
        extra_kwargs = {
            'password': {'write_only': True}
            }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match !')
        if CustomUser.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'Error': 'Email already exists'})

        user = CustomUser(email=self.validated_data['email'],
                          username=self.validated_data['email'],
                          birth_day=self.validated_data['birth_day'],
                          can_be_shared=self.validated_data['can_be_shared'],
                          can_be_contacted=self.validated_data['can_be_contacted'],
                          )

        user.set_password(data['password'])
        user.save()

        return user


class CustomUserListSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    customusers = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['email', 'birth_day', 'can_be_shared', 'can_be_contacted', 'password', 'confirm_password']
        extra_kwargs = {"password": {"write_only": True}}

    def get_customusers(self, instance):

        queryset = instance.customusers.filter(active=True)
        serializer = CustomUserListSerializer(queryset, many=True)
        return serializer.data


class CustomUserDetailSerializer(serializers.ModelSerializer):
    pass


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    pass


class CustomUserDeleteSerializer(serializers.ModelSerializer):
    pass


class CustomUSerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
