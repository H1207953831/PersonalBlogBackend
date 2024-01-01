"""
URL configuration for myblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from account.views import *
from article.views import *
from comment.views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = DefaultRouter()
router.register(r'article', ArticleViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'tag', TagViewSet)
router.register(r'avatar', AvatarViewSet)
router.register(r'comment',CommentViewSet)
router.register(r'user',UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include(router.urls)),
    path('api/token/',CustomUserTokenPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomUserTokenRefreshview.as_view(), name='token_refresh'),
    path('api/generate_verify_code/',generate_verify_code,name='generate_verify_code')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)