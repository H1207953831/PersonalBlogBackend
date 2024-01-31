from celery import shared_task
from django.core.cache import cache
from .models import ShangPin
from .serializers import ProductionDetailSerializer
@shared_task
def updata2database(uniqueID):
    instance = ShangPin.objects.get(uniqueID=uniqueID)
    data = cache.get(uniqueID,None)
    if data is None:
        return
    serializer = ProductionDetailSerializer(instance,data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)


@shared_task
def delete_database(uniqueID):
    instance = ShangPin.objects.get(uniqueID=uniqueID)
    data = cache.get(uniqueID)
    serializer = ProductionDetailSerializer(instance,data=data)
    if serializer.is_valid():
        serializer.save()
        cache.delete(uniqueID)
    else:
        print(serializer.errors)