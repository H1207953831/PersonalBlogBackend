# Generated by Django 4.2.7 on 2024-01-23 22:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_shangpin_image_alter_shangpin_uniqueid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shangpin',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='商品描述'),
        ),
        migrations.AlterField(
            model_name='shangpin',
            name='parameters',
            field=models.TextField(blank=True, null=True, verbose_name='商品参数'),
        ),
        migrations.AlterField(
            model_name='shangpin',
            name='uniqueID',
            field=models.CharField(default=uuid.UUID('721c5bce-efd1-4dde-8f8c-3e7737cd2291'), max_length=256, verbose_name='商品id'),
        ),
    ]
