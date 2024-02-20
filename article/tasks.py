from celery import shared_task
from django.core.cache import cache
from rest_framework.test import APIRequestFactory
import json
from django.http import HttpResponse
from rest_framework.response import Response
from .models import Article,Category
from .serializers import ArticleDetailSerializer

@shared_task
def update_database():
    articles = Article.objects.all()
    for article in articles:
        views = cache.get(f'article_{article.id}_views', article.views)
        article.views = views
        article.save()


@shared_task
def save_views(article_id):
    instance = Article.objects.filter(id=article_id).first()
    if instance:
        data = cache.get(f'article_{article_id}_key',None)
        if data:
            serializer = ArticleDetailSerializer(instance,data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(f'数据错误: {article_id}')
        else:
            print(f'数据丢失: {article_id}')
    else:
        print(f'文章不存在: {article_id}')
@shared_task
def count_category():
    categories = Category.objects.all()
    for category in categories:
        category.article_count = Article.objects.filter(category=category).count()
        category.save()
@shared_task
def reflash_cache():
    if cache.get('/api/article/',None) is None:
        from .views import ArticleViewSet
        factory = APIRequestFactory()
        request = factory.get('/api/article/')
        view = ArticleViewSet.as_view({'get': 'list'})
        response = view(request)
        response.status_code = 200
        response.render()
        cache.set('/api/article/', response, timeout=24 * 60 * 60)
        #print(1)
    else:
        print('缓存已存在')