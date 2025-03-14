# Generated by Django 4.2.7 on 2023-12-04 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_verifyemail_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='nickname',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='昵称'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True, verbose_name='用户'),
        ),
    ]
