from rest_framework import serializers
from .models import CustomUser, Project, Issue, Comment


class CommentSerializer(serializers.ModelSerializer):
    '''Serializer for Comments data serialization'''

    class Meta:
        model = Comment
        # fields = ['uuid', 'author', 'issue', 'issue_url', 'description', 'created_date']
        fields = ['uuid', 'issue_url', 'description', 'created_date']

    def create(self, validated_data, *args, **kwargs):
        issue = Issue.objects.get(id=self.context['issue_pk'])
        if issue:
            # test if connected user is in project contributor list
            if not issue.project.contributors.filter(id=self.context['request'].user.id).exists():
                raise serializers.ValidationError("Connected user unauthorized")
            validated_data['issue_ref'] = issue
            validated_data['author'] = self.context['request'].user
            instance = Comment.objects.create(**validated_data)
            return instance
        else:
            raise serializers.ValidationError("Data not valid")


class CommentListSerializer():
    '''Serializer for Comments data serialization'''

    class Meta:
        model = Comment
        fields = ['uuid',  'created_date']
