# Generated by Django 4.2.7 on 2023-12-13 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0008_article_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.CharField(default='1fde31f9d0074e33a19d96a85ce379b6', max_length=128, unique=True),
        ),
    ]
