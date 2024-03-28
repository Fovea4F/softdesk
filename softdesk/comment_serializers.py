from rest_framework import serializers
from .models import Issue, Comment


class CommentSerializer(serializers.ModelSerializer):
    '''Serializer for Comments data serialization'''

    class Meta:
        model = Comment
        # fields = ['uuid', 'author', 'issue', 'issue_url', 'description', 'created_date']
        fields = ['uuid', 'issue_url', 'description', 'created_date']

    '''def create(self, validated_data, *args, **kwargs):
        issue = Issue.objects.get(id=self.context['issue_pk'])
        if issue:
            # test if connected user is in project contributor list
            user = self.context['request'].user
            if not issue.project.contributors.filter(id=user.id).exists():
                raise serializers.ValidationError("Connected user unauthorized")
            validated_data['issue_ref'] = issue
            validated_data['author'] = self.context['request'].user
            instance = Comment.objects.create(**validated_data)
            return instance
        else:
            raise serializers.ValidationError("Data not valid")'''

    def validate_validated_data(self, validated_data, *args, **kwargs):
        issue = Issue.objects.get(id=self.context['issue_pk'])
        if issue:
            # test if connected user is in project contributor list
            user = self.context['request'].user
            if not issue.project.contributors.filter(id=user.id).exists():
                raise serializers.ValidationError("Connected user unauthorized")
            validated_data['issue_ref'] = issue
            validated_data['author'] = self.context['request'].user
            validated_data['in_charge'] = issue.assigned_contributor
            return validated_data


class CommentListSerializer(serializers.ModelSerializer):
    '''Serializer for Comments data serialization'''

    class Meta:
        model = Comment
        fields = ['uuid', 'issue_url']
