from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article, Category

@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
def update_category_count(sender, instance, **kwargs):
    # 统计每个 Category 下的文章数量
    categories = Category.objects.all()
    for category in categories:
        category.article_count = Article.objects.filter(category=category).count()
        category.save()