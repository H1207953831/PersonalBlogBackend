from django.db import models
import uuid
from account.models import CustomUser
from django.core.validators import MinValueValidator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# Create your models here.

def image_folder(instance, filename):
    new_filename = f'{instance.uniqueID}.{filename.split(".")[-1]}'
    return f'avatar/{new_filename}'
class ShangPin(models.Model):
    STATUS_DESCRIPT = [('0', '下架'), ('1', '在售'), ('2', '预售')]
    name = models.CharField(max_length=100, verbose_name='商品名称')
    exits = models.IntegerField(default=0, verbose_name='库存',validators=[MinValueValidator(0)])
    uniqueID = models.CharField(max_length=36, default=uuid.uuid4, verbose_name='商品id',primary_key=True)
    price = models.FloatField(max_length=128, default=0.01,validators=[MinValueValidator(0.01)], verbose_name='价格')
    category = models.CharField(max_length=128, verbose_name='商品分类')
    status = models.CharField(max_length=1, choices=STATUS_DESCRIPT, verbose_name='商品状态')
    image = models.ImageField(upload_to=image_folder,blank=True,null=True,verbose_name='商品图片')
    parameters = models.TextField(blank=True,null=True,verbose_name='商品参数')
    description = models.TextField(blank=True,null=True, verbose_name='商品描述')

class File(models.Model):
    name = models.CharField(max_length=100, verbose_name='文件名称')
    create = models.DateTimeField(auto_now_add=True)
    re_name = models.CharField(max_length=128, verbose_name='重命名')
    file_size = models.IntegerField(verbose_name='文件大小')
    file = models.FileField(upload_to='file/%Y%m%d/')
    author = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name='files')

