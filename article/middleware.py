from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

class SimpleCacheMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'GET':
            cache_key = request.get_full_path()
            response = cache.get(cache_key, None)
            if response is not None:
             return response

    def process_response(self,request, response):
        pass
        #cache_key = request.get_full_path()
        #cache.set(cache_key, response,timeout=24*60*60)
        return response
