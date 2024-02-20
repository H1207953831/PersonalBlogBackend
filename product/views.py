from django.core.cache import cache
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import ProductionSerializer, ProductionDetailSerializer, FilesSerializer
from .models import ShangPin, File
from rest_framework.response import Response
from myblog import celery_app as celery
from .tasks import updata2database, delete_database
from datetime import datetime, timedelta
from django.http import FileResponse

# Create your views here


class ProductionViewSet(viewsets.ModelViewSet):
    queryset = ShangPin.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = 'uniqueID'

    def get_serializer_class(self):
        if self.action in 'list':
            return ProductionSerializer
        else:
            return ProductionDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        uniqueID = kwargs.get('uniqueID')
        delay_uniqueID = f'{uniqueID}_delayID'
        data = cache.get(uniqueID, None)
        delayID = cache.get(delay_uniqueID, None)
        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
        cache.set(uniqueID, data, timeout=24 * 60 * 60)
        if delayID is not None:
            celery.control.revoke(delayID)
        delay_task = updata2database.apply_async((uniqueID,),
                                                 eta=datetime.utcnow() + timedelta(hours=23, minutes=58))
        cache.set(delay_uniqueID, str(delay_task.id), timeout=24 * 60 * 60)
        return Response(data)


class BuyProduct(APIView):
    # 假设是一个视图函数,同时还有对应的订单序列化和models

    def post(self, request):
        product_id = request.data.get('product_id', None)
        product_count = request.data.get('product_count', None)
        # 判断参数死不是合法的
        if product_id is None or product_count is None:
            data = {'params lost': '缺少关键参数: product_id,product_count'}
            return Response(data=data, status=501)
        if not is_positive_integer(product_count):
            data = {'params error': 'product_count必须是大于等于1的正整数'}
            return Response(data=data, status=403)
        lockid = f'lock:{product_id}'
        lock = cache.lock(lockid, timeout=10)
        have_lock = False
        try:
            have_lock = lock.acquire(blocking=True)
            if have_lock:
                product = cache.get(product_id, None)
                if product is None or product['exits'] == 0:
                    data = {'message': '商品已卖完'}
                    return Response(data=data, status=404)
                elif product['exits'] >= int(product_count):
                    product['exits'] -= int(product_count)
                    if product['exits'] == 0:
                        delete_database.apply_async((product_id,), eta=datetime.utcnow() + timedelta(minutes=1))
                else:
                    data = {'message':'超过最大库存,无法购买'}
                    return Response(data, status=200)
                cache.set(product_id, product, timeout=24*60*60)
                data = {'message':'购买成功'}
                return Response(data, status=200)
        finally:
            # 只有获得锁才能释放
            if have_lock:
                lock.release()


def is_positive_integer(value):
    # 判断值是不是正整数
    if isinstance(value, int) and value > 0:
        return True
    elif isinstance(value, str) and value.isdigit() and int(value) > 0:
        return True
    else:
        return False

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

import time

def file_iterators(filename,chunk_size=1024*100, time_interval=1):
    while True:
        c = filename.read(chunk_size)
        if c:
            yield c
            time.sleep(time_interval)
        else:
            break

class FilesViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FilesSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 're_name'
    def retrieve(self, request, *args, **kwargs):
        # 获取文件对象
        instance = self.get_object()
        # 判断是否获取文件详细信息还是下载文件
        if request.query_params.get('download') == 'true':
            file = open(instance.file.path, 'rb')
            # 设置文件名称
            response = FileResponse(file_iterators(file))
            response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(instance.name)
            # 设置文件大小
            response['Content-Length'] = instance.file_size
            return response
        else:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

