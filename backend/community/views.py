from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from books.models import Book
from .models import ChatMessage
from .serializers import ChatMessageSerializer

# 함께 읽어요 채팅: 조회는 누구나, 생성은 로그인한 유저만 
class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        isbn = self.kwargs.get('isbn')
        return ChatMessage.objects.filter(book__isbn=isbn).select_related('user') 

    def perform_create(self, serializer):
        isbn = self.kwargs.get('isbn')
        book = get_object_or_404(Book, isbn=isbn)
        serializer.save(user=self.request.user, book=book)