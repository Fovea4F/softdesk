from rest_framework import serializers

from .models import Issue, Project, CustomUser


class IssueSerializer(serializers.ModelSerializer):
    '''Serializer for Projects entities Listing'''

    class Meta:
        model = Issue
        fields = ['name', 'author', 'assigned_contributor', 'project', 'issue_type', 'priority',
                  'status', 'description', 'created_date']

    def validate_assigned_contributor(self, value):
        '''Verify if assigned_contributor is valid for this Issue'''
        project = self.instance.project
        project_contributors = project.contributors.all()
        if value not in project_contributors:
            raise serializers.ValidationError("Assigned contributor unknown in project")
        return value


class IssueCreateSerializer(serializers.ModelSerializer):
    '''Serializer for Issue Creation'''
    assigned_contributor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)

    class Meta:

        model = Issue
        fields = ['name', 'assigned_contributor', 'issue_type', 'priority', 'description']

    def create(self, validated_data, *args, **kwargs):
        project_id = int(self.context['view'].kwargs['project_pk'])
        if project_id:
            validated_data['project'] = Project.objects.get(id=project_id)
            if 'assigned_contributor' not in validated_data:
                validated_data['assigned_contributor'] = self.context['request'].user
            # test if assigned_contributor is listed in project contributors
            if not validated_data['project'].contributors.filter(id=validated_data['assigned_contributor'].id).exists():
                raise serializers.ValidationError("Assigned contributor unknown in project")
            instance = Issue.objects.create(**validated_data)
            return instance
        else:
            raise serializers.ValidationError("Data not valid")


class IssueListSerializer(serializers.ModelSerializer):
    '''Serializer used for Issues list'''

    class Meta:
        model = Issue
        fields = ['id', 'author', 'name']
