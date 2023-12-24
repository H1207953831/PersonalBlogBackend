from django.db import models
#from django.contrib.auth.models import User
from account.models import CustomUser
from django.utils import timezone
from article.models import Article


# Create your models here.
class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey(
        'self',on_delete=models.SET_NULL,
        blank=True,null=True,related_name='children'
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.content[:20]
