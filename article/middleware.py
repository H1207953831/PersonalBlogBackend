import re
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from rest_framework.response import Response


class SimpleCacheMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'GET':
            cache_key = request.get_full_path()
            match = re.search(r'^/api/article/\d+/',cache_key)
            if match is None:
                response = cache.get(cache_key, None)
                if response:
                    return response

    def process_response(self, request, response):
        check_list = ['test','product','media','file',]
        if any(item in request.get_full_path() for item in check_list):
            return response
        else:
            cache_key = request.get_full_path()
            match = re.search(r'^/api/article/\d+/',cache_key)
            if match is None and response.status_code == 200:
                if cache.get(cache_key,None) is None:
                    cache.set(cache_key, response, timeout=24 * 60 * 60)
            return response
