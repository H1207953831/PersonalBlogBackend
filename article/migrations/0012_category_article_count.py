# Generated by Django 4.2.7 on 2023-12-17 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0011_article_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='article_count',
            field=models.IntegerField(default=0),
        ),
    ]
