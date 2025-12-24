from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from books.models import Book
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from books.serializers import BookListSerializer
from django.db.models import Count


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

class MyActivityListView(APIView):
    # 로그인한 사람만 접근 가능
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. 내가(request.user) 메시지(messages)를 남긴 책들을 중복 없이(distinct) 가져옴
        books = Book.objects.filter(messages__user=request.user).distinct()
        
        # 2. 기존에 쓰던 책 목록 시리얼라이저로 예쁘게 포장
        serializer = BookListSerializer(books, many=True, context={'request': request})
        
        # 3. 데이터 반환
        return Response(serializer.data)

class ActiveCommunityListView(APIView):
    permission_classes = [permissions.AllowAny] # 누구나 볼 수 있게

    def get(self, request):
        # 채팅 메시지가 많은 순으로 3개 추출
        active_books = Book.objects.annotate(
            message_count=Count('messages'),
            user_count=Count('messages__user', distinct=True)
        ).filter(message_count__gt=0).order_by('-message_count')[:3]
        
        data = [{
            'isbn': b.isbn,
            'title': b.title,
            'message_count': b.message_count,
            'user_count': b.user_count
        } for b in active_books]
        
        return Response(data)