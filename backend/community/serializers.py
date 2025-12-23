from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    created_at = serializers.DateTimeField(read_only=True) 

    class Meta:
        model = ChatMessage
        fields = ['id', 'user_id', 'nickname', 'content', 'created_at']
        read_only_fields = ['user']