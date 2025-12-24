from rest_framework import serializers
from .models import ChatMessage, TradeChatRoom, TradeMessage

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

class TradeChatRoomSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    opponent_nickname = serializers.SerializerMethodField()

    class Meta:
        model = TradeChatRoom
        fields = ['id', 'book_title', 'book_author', 'status', 'opponent_nickname', 'created_at']

    def get_opponent_nickname(self, obj):
        user = self.context['request'].user
        return obj.buyer.nickname if obj.seller == user else obj.seller.nickname