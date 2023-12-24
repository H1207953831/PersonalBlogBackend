# Generated by Django 4.2.7 on 2023-11-21 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_category_alter_article_options_article_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='article', to='article.tag'),
        ),
    ]
