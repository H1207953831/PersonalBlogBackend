from rest_framework import serializers, status
from .models import Article, Category, Tag, Avatar
from account.serializers import UserDescSerializer
from comment.serializers import CommentSerializer
from rest_framework.response import Response
import re

class AvatarSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='avatar-detail')

    class Meta:
        model = Avatar
        fields = '__all__'


class TagSerializer(serializers.HyperlinkedModelSerializer):

    def check_tag_obj_exists(self, validated_data):
        text = validated_data.get('text')
        if Tag.objects.filter(text=text).exists():
            raise serializers.ValidationError("Tag with text {} already exists.".format(text))

    def create(self, validated_data):
        self.check_tag_obj_exists(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.check_tag_obj_exists(validated_data)
        return super().update(instance, validated_data)

    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category-detail')
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['created']


class ArticleBaseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author = UserDescSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_det = serializers.CharField(write_only=True, allow_null=True, required=False)
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
        slug_field='text',
    )
    avatar = AvatarSerializer(read_only=True)
    avatar_id = serializers.IntegerField(
        write_only=True,
        allow_null=True,
        required=False,
    )
    comments = CommentSerializer(many=True, read_only=True)

    default_error_messages = {
        'incorrect_avatar_id': 'Avatar with id {value} not exists.',
        'incorrect_category_id': 'Category with id {value} not exists.',
        'default': 'No more message here..',
    }


    def check_obj_exists_or_fail(self, model, value, message='default'):
        if not self.default_error_messages.get(message, None):
            message = 'default'

        if not model.objects.filter(value=value).exists() and value is not None:
            self.fail(message, value=value)

    def validate_category_det(self, value):
        return value

    def to_internal_value(self, data):
        tags_data = data.get('tags')
        if isinstance(tags_data, list):
            for text in tags_data:
                if not Tag.objects.filter(text=text).exists():
                    Tag.objects.create(text=text)
        return super().to_internal_value(data)

    def _get_category(self, validated_data):
        category_detail = validated_data.pop('category_det', None)
        if category_detail is None:
            return None
        try:
            if category_detail.isdigit():
                return Category.objects.get(id=category_detail)
            else:
                return Category.objects.get_or_create(title=category_detail)[0]
        except Category.DoesNotExist:
            raise serializers.ValidationError('Category not found.')

    def validate(self, attrs):
        allow_fields = ['category_det','tags','title','body']
        for key in attrs.keys():
            if key not in  allow_fields:
                raise serializers.ValidationError(f"字段 {key} 不是允许的字段。")
        return attrs

    def create(self, validated_data):
        category = self._get_category(validated_data)
        if category:
            validated_data['category'] = category
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category = self._get_category(validated_data)
        if category:
            validated_data['category'] = category
        return super().update(instance, validated_data)


class ArticleCategoryDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='article-detail')

    class Meta:
        model = Article
        fields = [
            'url','id', 'title'
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    article = ArticleCategoryDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'title', 'created', 'article'
        ]


class ArticleSerializer(ArticleBaseSerializer):
    body_html = serializers.SerializerMethodField()

    def get_body_html(self, obj):
        return obj.body.split('\n')[0].replace('`','')

    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {'body': {'write_only': True}}


class ArticleDetailSerializer(ArticleBaseSerializer):
    id = serializers.IntegerField(read_only=True)
    comment = CommentSerializer(many=True, read_only=True)

    views = serializers.SerializerMethodField()

    def get_views(self, obj):
        obj.views += 1
        obj.save()
        return obj.views

    class Meta:
        model = Article
        fields = '__all__'
