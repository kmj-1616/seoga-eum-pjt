from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from django.shortcuts import get_object_or_404
from books.models import Book
from .models import ChatMessage, TradeChatRoom, TradeMessage
from .serializers import ChatMessageSerializer, TradeMessageSerializer, TradeChatRoomSerializer
from books.serializers import BookListSerializer
from django.db.models import Count, OuterRef, Subquery


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
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 1. 각 도서(Book)의 PK와 연결된 메시지 중 가장 최근 것 1개의 내용(content)만 추출
        latest_msg = ChatMessage.objects.filter(
            book=OuterRef('pk')
        ).order_by('-created_at').values('content')[:1]

        # 2. 책 목록을 가져오면서 위 서브쿼리를 'last_message'라는 이름으로 붙임
        active_books = Book.objects.annotate(
            message_count=Count('messages'),
            user_count=Count('messages__user', distinct=True),
            last_message_content=Subquery(latest_msg) 
        ).filter(message_count__gt=0).order_by('-message_count')[:3]
        
        data = [{
            'isbn': b.isbn,
            'title': b.title,
            'message_count': b.message_count,
            'user_count': b.user_count,
            'last_message': b.last_message_content 
        } for b in active_books]
        
        return Response(data)
    
class TradeMessageView(APIView):
    def get(self, request, trade_id):
        messages = TradeMessage.objects.filter(room_id=trade_id).order_by('created_at')
        serializer = TradeMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, trade_id):
        room = TradeChatRoom.objects.get(id=trade_id)
        serializer = TradeMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, room=room)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class MyTradeChatRoomListView(generics.ListAPIView):
    """현재 유저가 참여 중인 1:1 거래 채팅방 목록 조회"""
    serializer_class = TradeChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 내가 판매자이거나 구매자인 방을 모두 찾음
        return TradeChatRoom.objects.filter(
            Q(seller=user) | Q(buyer=user)
        ).select_related('book', 'seller', 'buyer').order_by('-created_at')
    
class CreateTradeRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, isbn):
        # 1. 해당 도서와 소장자(판매자) 정보 확인
        book = get_object_or_404(Book, isbn=isbn)
        
        # 소장자 찾기 (UserBookStock 모델 기준)
        # 만약 여러 명이라면 특정 판매자를 지정해야 하나, 여기서는 예시로 첫 번째 소장자를 타겟팅합니다.
        seller_stock = book.userbookstock_set.first() 
        if not seller_stock:
            return Response({"error": "소장자가 없는 도서입니다."}, status=400)
        
        seller = seller_stock.user
        buyer = request.user

        if seller == buyer:
            return Response({"error": "본인의 도서는 구매할 수 없습니다."}, status=400)

        # 2. 이미 두 사람 사이에 이 책으로 만든 방이 있는지 확인
        room, created = TradeChatRoom.objects.get_or_create(
            book=book,
            seller=seller,
            buyer=buyer,
            defaults={'status': 'REQUESTED'}
        )

        # 3. 방 ID 반환
        return Response({
            "trade_id": room.id,
            "message": "채팅방이 생성되었습니다." if created else "기존 채팅방으로 이동합니다."
        }, status=201 if created else 200)