from rest_framework import serializers
from account.serializers import UserDescSerializer
from .models import Comment


class CommentChildrenSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='comment-detail')
    author = UserDescSerializer

    class Meta:
        model = Comment
        exclude = [
            'parent',
            'article',
        ]


class CommentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='comment-detail')
    author = UserDescSerializer(read_only=True)

    article = serializers.HyperlinkedRelatedField(view_name='article-detail', read_only=True)
    article_id = serializers.IntegerField(write_only=True, allow_null=False,required=True)

    parent = CommentChildrenSerializer(read_only=True)
    parent_id = serializers.IntegerField(write_only=True,allow_null=True,required=False)

    def update(self, instance, validated_data):
        validated_data.pop('parent_id',None)
        return super().update(instance, validated_data)

    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {'created': {'read_only': True}}
