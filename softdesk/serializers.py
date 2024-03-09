from rest_framework import serializers
from datetime import date
from .models import CustomUser, Project


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    can_be_contacted = serializers.BooleanField(default=False)
    can_be_shared = serializers.BooleanField(default=False)
    # authorized_age = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'birthday', 'can_be_contacted',
                  'can_be_shared', 'password', 'confirm_password']

    def validate_password(self, password):
        # verify if 2 given passwords match
        confirm_password = self.initial_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError(
                    'error: passwords are not equals')
        else:
            raise serializers.ValidationError(
                'error: password information is mandatory')
        return password

    def validate_birthday(self, birthday):
        # verify if Customer is authorized to register
        today = date.today()
        authorized_age = 15
        age = today.year - birthday.year - \
            ((today.month, today.day) < (birthday.month, birthday.day))
        if age < authorized_age:
            raise serializers.ValidationError(
                f'You must be {authorized_age} years old to register.'
            )
        return birthday

    def update(self, instance, validated_data):
        instance.username = validated_data.get('email', instance.email)
        instance.email = validated_data.get('email', instance.email)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.can_be_shared = validated_data.get(
            'can_be_shared', instance.can_be_shared)
        instance.can_be_contacted = validated_data.get(
            'can_be_contacted', instance.can_be_contacted)
        instance.set_password(validated_data.get(
            'password', instance.password))
        instance.save()
        return instance

    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.get('email')
        user = CustomUser.objects.create_user(
            username=username,
            email=validated_data.get('email'),
            birthday=validated_data.get('birthday'),
            can_be_contacted=validated_data.get('can_be_contacted'),
            can_be_shared=validated_data.get('can_be_shared')
        )
        user.set_password(password)
        user.save()
        return user


class CustomUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'contributors',
                  'project_type', 'description', 'created_date']

    def create(self, validated_data):
        # Create the instance without saving it yet
        author = self.context['request'].user
        # Transform users list in users_id list
        contributors = validated_data.pop('contributors')
        contributors_ids = [contributor.id for contributor in contributors]
        instance = Project.objects.create(**validated_data)
        instance.contributors.set([author])
        # add every contributor id present in the list
        instance.contributors.add(*contributors_ids)
        return instance


class ProjectListSerializer(serializers.ModelSerializer):
    ''' Limited information for Project List '''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author']


class ProjectDetailSerializer(serializers.ModelSerializer):
    '''Serializer for Projects Detail'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'contributors',
                  'project_type', 'description', 'created_date']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    '''Serializer for Projects Update'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'project_type',
                  'description', 'created_date']
