from django.shortcuts import render
from rest_framework import generics, permissions
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # URL에서 book_id를 받아 해당 도서의 메시지만 필터링
        book_id = self.kwargs.get('book_id')
        return ChatMessage.objects.filter(book_id=book_id)

    def perform_create(self, serializer):
        # 현재 로그인한 유저와 URL의 book_id를 자동 저장
        book_id = self.kwargs.get('book_id')
        serializer.save(user=self.request.user, book_id=book_id)