import time
from django.core.cache import cache
from django.http import HttpResponse,HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
class RestrictedMiddleware(MiddlewareMixin):
    def process_request(self, request):
        url = request.path
        if url.startswith('/api/'):
            ip = request.META.get('REMOTE_ADDR')
            black_list = cache.get('blacklist',[])
            if ip in black_list:
                return HttpResponseForbidden('大佬，别爬了::>_<::')

            requests = cache.get(ip,[])

            while requests and time.time() - requests[-1] > 60:
                requests.pop()

            requests.insert(0,time.time())
            cache.set(ip, requests, timeout=60)
            if len(requests) > 80:
                black_list.append(ip)
                cache.set('blacklist',black_list,timeout=3*60*60*24)
                return HttpResponseForbidden('哦豁，大佬，访问太快，小黑屋3天哦~')

            if len(requests) > 40:
                return HttpResponseForbidden(f'访问慢点，已经被警告了：再有{20-len(requests)}次就要被拉进去小黑屋了~')

class TholltMiddleware(MiddlewareMixin):
    def process_request(self,request):
        max_connections = getattr(settings, 'MAX_CONNECTIONS', 200)
        connections = cache.get('connections',{})
        if sum(connections.values()) >= max_connections:
            return HttpResponseForbidden('超过最大连接数，请稍后再试~')
        ip_address = request.META.get('REMOTE_ADDR')
        current_connection = connections.get(ip_address,0)
        connections[ip_address] = current_connection + 1
        cache.set('connections',connections)

    def process_response(self,request,response):
        ip_address = request.META.get('REMOTE_ADDR')
        connections = cache.get('connections',{})
        if ip_address in connections:
            connections[ip_address] -= 1
            if connections[ip_address] <= 0:
                del connections[ip_address]
            cache.set('connections',connections)
        return response
        pass
