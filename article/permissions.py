from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            '''这里的safe请求方法分别是'GET', 'HEAD', 'OPTIONS'''
            return True
        return request.user.is_superuser
