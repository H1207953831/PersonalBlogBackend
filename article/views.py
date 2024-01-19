from rest_framework.generics import get_object_or_404
from .models import Article, Category, Tag, Avatar
from .serializers import ArticleSerializer, ArticleDetailSerializer, ArticleCategoryDetailSerializer
from .serializers import CategoryDetailSerializer, CategorySerializer
from .serializers import TagSerializer
from .serializers import AvatarSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import filters
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.http import FileResponse
from .utils import file_iterators
from io import BytesIO
from urllib.parse import quote
from django.core.cache import cache
from .tasks import save_views
from django.utils import timezone

# Create your views here.

class Pagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['body', 'title']
    pagination_class = Pagination
    page_size = 10

    @action(detail=False, methods=['get'])
    def latest_articles(self, request):
        article_list = Article.objects.all().order_by('-created')[:10]
        article_list_serializer = ArticleCategoryDetailSerializer(article_list, many=True, context={'request': request})
        return Response(article_list_serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def popular_titles(self, request):
        titles = Article.objects.all().order_by('-views')[:10]
        titles_serializer = ArticleCategoryDetailSerializer(titles, many=True, context={'request': request})
        return Response(titles_serializer.data)

    @action(detail=False, methods=['get'])
    def popular_articles(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-views')
        page = self.paginate_queryset(queryset)
        if page is not None:
            popular_articles_serializer = ArticleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(popular_articles_serializer.data)
        popular_articles_serializer = ArticleSerializer(queryset, many=True, context={'request': request})
        return Response(popular_articles_serializer.data)

    @action(detail=False, methods=['get'])
    def category_articles(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        category_id = request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category=category_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            category_articles = ArticleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(category_articles.data)
        category_articles = ArticleSerializer(queryset, many=True, context={'request': request})
        return Response(category_articles)

    @action(detail=False, methods=['get'])
    def test(self,request):
        return Response({'message':'测试'})

    def get_serializer_class(self):
        if self.action in 'list':
            return ArticleSerializer
        else:
            return ArticleDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        article_cache_key = f"article_{kwargs.get('pk')}_key"
        views_cache_key = f"article_{kwargs.get('pk')}_views"
        data = cache.get(article_cache_key, None)
        views = cache.get(views_cache_key, None)
        if data is None or views is None:
            instance = self.get_object()
            instance.views += 1
            views = max(instance.views,views) if views is not None else instance.views
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(article_cache_key, data, timeout=24 * 60 * 60)
        else:
            views += 1
        cache.set(views_cache_key, views, timeout=24 * 60 * 60)
        save_views.apply_async((kwargs.get('pk'),), eta=timezone.now()+ timezone.timedelta(hours=23,minutes=59))
        data['views'] = views
        return Response(data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return CategorySerializer
        else:
            return CategoryDetailSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]

    pagination_class = None


class AvatarViewSet(viewsets.ModelViewSet):
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = [IsAdminOrReadOnly]


class ArticleDownloadViewSet(APIView):

    def get(self, request, *args, **kwargs):
        if request.GET.get('article'):
            article = get_object_or_404(Article, pk=request.GET.get('article'))
            mem_file = BytesIO(article.body.encode('utf-8'))
            file_name_encoded = quote((article.title + '.md').encode('utf-8'))
            response = FileResponse(file_iterators(mem_file), as_attachment=True)
            response['Content-Length'] = len(mem_file.getvalue())
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(file_name_encoded)
            return response
        else:
            return Response({"detail": "传递参数有误"}, status=status.HTTP_404_NOT_FOUND)
