from django.db import models
from django.utils import timezone
from account.models import CustomUser
from markdown import Markdown
from django.urls import reverse
import uuid


# Create your models here.

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(default=timezone.now)
    article_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Tag(models.Model):
    text = models.CharField(max_length=30)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.text


class Avatar(models.Model):
    content = models.ImageField(upload_to='avatar/%Y%m%d%H%M%S')


class Article(models.Model):
    author = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name='article')

    title = models.CharField(max_length=300, verbose_name='文章标题')
    body = models.TextField(verbose_name='文章内容')
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='article'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='article')
    avatar = models.ForeignKey(
        Avatar,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='article'
    )
    views = models.IntegerField(default=0, verbose_name='浏览量')

    def get_md(self):
        md = Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
            ]
        )
        md_body = md.convert(str(self.body))
        return md_body, md.toc

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title
