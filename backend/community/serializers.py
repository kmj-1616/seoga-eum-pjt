from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    # 유저의 ID 대신 닉네임을 화면에 표시 
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    # 날짜 형식을 "오전 10:30" 형식으로 포맷팅 (Django 설정을 한국어로 했을 때)
    created_at = serializers.DateTimeField(format="%p %I:%M", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'user_id', 'nickname', 'content', 'created_at']
        read_only_fields = ['user'] # 유저는 View에서 request.user로 직접 저장