# Generated by Django 4.2.7 on 2024-01-27 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='file/%Y%m%d/'),
        ),
    ]
