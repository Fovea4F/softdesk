from rest_framework import serializers

from .models import Project, CustomUser


class ProjectSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'contributors', 'project_type', 'description']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'project_type', 'description']

    def validate(self, data):
        return data

'''    def validate_contributors(self, value):
        # Manage ManyToMany Field update
        print('------------------------------------------')
        print(f'self : {self}')
        print('------------------------------------------')
        print(f'value : {value}')
        print('------------------------------------------')
        contributors = value.pop('contributors', None)
        print(contributors)
        if contributors is not None:
            self.contributors.set(contributors)

        return value'''


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


class ProjectNullSerializer(serializers.ModelSerializer):
    '''Limited information for Project List'''

    class Meta:
        model = Project
        fields = []


class ProjectContributorSerializer(serializers.ModelSerializer):
    '''Serializer for Projects Contributors List Update'''
    class Meta:
        model = Project
        fields = ('id', 'contributors')

    def validate_contributor_id(self, data):
        # Check if the contributor exists
        contributor_id = self.context['contributor_id']
        try:
            CustomUser.objects.get(pk=contributor_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid contributor ID")
        return contributor_id
