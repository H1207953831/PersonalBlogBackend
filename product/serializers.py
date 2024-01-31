from rest_framework import serializers
from rest_framework.reverse import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ShangPin, File
from account.serializers import UserDescSerializer
import uuid

class ProductionSerializer(serializers.ModelSerializer):
    uniqueID_url = serializers.SerializerMethodField()
    class Meta:
        model = ShangPin
        fields = '__all__'

    def get_uniqueID_url(self, obj):
        return reverse('shangpin-detail', kwargs={'uniqueID':obj.uniqueID}, request=self.context.get('request'))
class ProductionDetailSerializer(ProductionSerializer):
    pass


class FilesSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    name = serializers.CharField(default='')
    re_name = serializers.CharField(default='')
    file_size = serializers.IntegerField(default=0)
    author = UserDescSerializer(read_only=True)
    class Meta:
        model = File
        fields = '__all__'

    def get_url(self,obj):
        return reverse('file-detail', args=[obj.re_name], request=self.context.get('request'))
    def create(self, validated_data):
        upload_file = validated_data.pop('file')
        validated_data['re_name'] = uuid.uuid4()
        validated_data['name'] = upload_file.name
        validated_data['file_size'] = upload_file.size
        path = default_storage.save(validated_data['re_name'], ContentFile(upload_file.read()))
        validated_data['file'] = path
        request = self.context.get('request', None)
        if request:
            validated_data['author'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        return super().update(instance, validated_data)