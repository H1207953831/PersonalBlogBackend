from celery import shared_task
from django.core.cache import cache
from .models import Article
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
    instance = Article.objects.get(id=article_id)
    data = cache.get(f'article_{article_id}_key',None)
    if data:
        serializer = ArticleDetailSerializer(instance,data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(f'数据错误: {article_id}')
    else:
        print(f'数据丢失: {article_id}')
