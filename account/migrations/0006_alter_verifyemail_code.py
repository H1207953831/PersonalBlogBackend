# Generated by Django 4.2.7 on 2023-12-04 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_remove_verifyemail_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifyemail',
            name='code',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='验证码'),
        ),
    ]
