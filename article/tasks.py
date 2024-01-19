from celery import shared_task
from django.core.cache import cache
from .models import Article


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
    views = cache.get(f'article_{instance.id}_views', instance.views)
    instance.views = max(views, instance.views)
    instance.save()
