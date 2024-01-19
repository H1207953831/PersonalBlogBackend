from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article, Category
from django.core.cache import cache

@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
def update_category_count(sender, instance, **kwargs):
    # 统计每个 Category 下的文章数量
    categories = Category.objects.all()
    for category in categories:
        category.article_count = Article.objects.filter(category=category).count()
        category.save()

    cache_keys = [
        '/api/category/',
        '/api/article/popular_titles/',
        '/api/article/latest_articles/',
        '/api/article/',
        f'/api/article/{instance.id}/',
        '/api/article/popular_articles/',
        f'/api/article/category_articles/?category={instance.category}'
    ]
    for cache_key in cache_keys:
        cache.delete(cache_key)
