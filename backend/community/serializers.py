from rest_framework import serializers
from .models import ChatMessage, TradeChatRoom, TradeMessage, TradeStatusRequest

class ChatMessageSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    created_at = serializers.DateTimeField(read_only=True) 

    class Meta:
        model = ChatMessage
        fields = ['id', 'user_id', 'nickname', 'content', 'created_at']
        read_only_fields = ['user']

class TradeMessageSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='sender.nickname', read_only=True)
    user_id = serializers.IntegerField(source='sender.id', read_only=True)

    class Meta:
        model = TradeMessage
        fields = ['id', 'user_id', 'nickname', 'content', 'created_at']

class TradeStatusRequestSerializer(serializers.ModelSerializer):
    requester_nickname = serializers.CharField(source='requester.nickname', read_only=True)
    requester_id = serializers.IntegerField(source='requester.id', read_only=True)
    
    class Meta:
        model = TradeStatusRequest
        fields = ['id', 'room_id', 'requester_id', 'requester_nickname', 'new_status', 'request_status', 'created_at']
        read_only_fields = ['requester', 'created_at']

class TradeChatRoomSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    opponent_nickname = serializers.SerializerMethodField()
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    buyer_id = serializers.IntegerField(source='buyer.id', read_only=True)
    selling_price = serializers.SerializerMethodField()
    pending_status_request = serializers.SerializerMethodField()

    class Meta:
        model = TradeChatRoom
        fields = ['id', 'book_title', 'book_author', 'status', 'opponent_nickname', 'seller_id', 'buyer_id', 'selling_price', 'pending_status_request', 'location', 'locker_number', 'created_at']

    def get_opponent_nickname(self, obj):
        user = self.context['request'].user
        return obj.buyer.nickname if obj.seller == user else obj.seller.nickname
    
    def get_selling_price(self, obj):
        # 판매자가 등록한 판매가를 UserBookStock에서 조회
        try:
            stock = obj.book.userbookstock_set.get(user=obj.seller)
            return stock.selling_price
        except:
            return 0
    
    def get_pending_status_request(self, obj):
        # 현재 대기 중인 상태 변경 요청 조회
        try:
            pending_request = obj.status_requests.filter(request_status='PENDING').first()
            if pending_request:
                return TradeStatusRequestSerializer(pending_request).data
        except:
            pass
        return None
        return None