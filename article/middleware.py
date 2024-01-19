import re
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from rest_framework.response import Response


class SimpleCacheMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'GET':
            cache_key = request.get_full_path()
            match = re.search(r'^/api/article/\d+',cache_key)
            if match is None:
                response = cache.get(cache_key, None)
                if response is not None:
                    return response

    def process_response(self, request, response):
        if 'test' in  request.get_full_path():
            return response
        else:
            cache_key = request.get_full_path()
            match = re.search(r'^/api/article/\d+',cache_key)
            if match is None:
                cache.set(cache_key, response, timeout=24 * 60 * 60)
            return response
