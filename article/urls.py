from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'article',views.ArticleViewSet)


app_name = 'article'

urlpatterns = [
]