from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    '''Serializer for Comments data serialization'''

    class Meta:
        model = Comment
        # fields = ['uuid', 'author', 'issue', 'issue_url', 'description', 'created_date']
        fields = ['uuid', 'author', 'issue_ref', 'issue_url', 'description', 'created_date']
        # read_only_fields = ['uuid', 'issue_url', 'created_date']


class CommentListSerializer(serializers.ModelSerializer):
    '''Serializer for Comments data serialization'''

    class Meta:
        model = Comment
        fields = ['uuid', 'issue_url']
