# Generated by Django 4.2.7 on 2023-12-04 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_alter_verifyemail_add_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(default='jack', max_length=128, unique=True, verbose_name='用户'),
        ),
    ]
