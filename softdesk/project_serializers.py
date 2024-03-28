from rest_framework import serializers

from .models import Project, CustomUser


class ProjectSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'status', 'contributors', 'project_type', 'description']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'project_type', 'description']


class ProjectListSerializer(serializers.ModelSerializer):
    ''' Limited information for Project List '''

    class Meta:
        model = Project
        fields = ['id', 'name', 'author']

    print('toto')


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
