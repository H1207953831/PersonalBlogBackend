from .models import Article, Category, Tag, Avatar
from .serializers import ArticleSerializer, ArticleDetailSerializer, ArticleCategoryDetailSerializer
from .serializers import CategoryDetailSerializer, CategorySerializer
from .serializers import TagSerializer
from .serializers import AvatarSerializer
from rest_framework import viewsets
from rest_framework import filters
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count

# Create your views here.

class Pagination(PageNumberPagination):
    def get_paginated_response(self,data):
        return Response({
            'count':self.page.paginator.count,
            'next':self.get_next_link(),
            'previous':self.get_previous_link(),
            'total_pages':self.page.paginator.num_pages,
            'current_page':self.page.number,
            'results':data
        })

        pass
    pass


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
    def home(self):
        pass
    def get_serializer_class(self):
        if self.action in 'list':
            return ArticleSerializer
        else:
            return ArticleDetailSerializer


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
