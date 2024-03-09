from rest_framework import serializers
from ..models import Project


class ProjectSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Project
        fields = ['id', 'name', 'project_type', 'description', 'created_date']

    '''def create(self, validated_data):
        # Create the instance without saving it yet
        author = self.context['request'].user
        # Transform users list in users_id list
        contributors = validated_data.pop('contributors')
        contributors_ids = [contributor.id for contributor in contributors]
        instance = Project.objects.create(**validated_data)
        instance.contributors.set([author])
        # add every contributor id present in the list
        instance.contributors.add(*contributors_ids)
        return instance'''


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


class ProjectContributorSerializer(serializers.ModelSerializer):
    '''Serializer for Projects Contributors List Update'''

    name = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'contributors']

    def contributors_add(self, validated_data):
        pass

        '''author = self.context['request'].user
        # Transform contributors list in contributors_id list
        contributors = validated_data.pop('contributors')
        contributors_ids = [contributor.id for contributor in contributors]
        instance = Project.objects.create(**validated_data)
        instance.contributors.set([author])
        # add every contributor id present in the list
        instance.contributors.add(*contributors_ids)
        return instance'''
