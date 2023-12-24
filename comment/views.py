from django.shortcuts import render
from .serializers import CommentSerializer
from rest_framework import viewsets
from .permissions import IsOwnerOrReadOnly
from .models import Comment
# Create your views here.


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)