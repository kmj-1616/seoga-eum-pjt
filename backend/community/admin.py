from django.contrib import admin
from .models import ChatMessage, TradeChatRoom, TradeMessage, TradeStatusRequest

@admin.register(TradeChatRoom)
class TradeChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'seller', 'buyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(TradeStatusRequest)
class TradeStatusRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'requester', 'new_status', 'request_status', 'created_at')
    list_filter = ('request_status', 'new_status', 'created_at')

@admin.register(TradeMessage)
class TradeMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'created_at')
    list_filter = ('created_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'user', 'created_at')
    list_filter = ('created_at',)
