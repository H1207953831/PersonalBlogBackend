from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.utils import timezone

# Create your models here.

class CustomUser(AbstractUser):
    username = models.CharField(verbose_name=_('用户'),max_length=128,unique=True)
    email = models.EmailField(verbose_name=_('邮箱'),unique=True)
    nickname = models.CharField(verbose_name=_('昵称'),max_length=30,blank=True,null=True)
    password = models.CharField(verbose_name=_('密码'),max_length=128)
    phone = models.CharField(verbose_name=_('手机'),max_length=15,unique=True,blank=True,null=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
    def __str__(self):
        return self.username


class VerifyEmail(models.Model):

    email = models.CharField(verbose_name=_('邮箱'),blank=True,max_length=20)
    #phone = models.CharField(verbose_name=_('手机'),blank=True,max_length=15)
    code = models.CharField(verbose_name=_('验证码'),max_length=8,blank=True,null=True)
    add_time = models.DateTimeField(verbose_name=_('创建时间'), default=timezone.now)
