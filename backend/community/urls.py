from django.urls import path
from .views import ChatMessageListCreateView, MyActivityListView, ActiveCommunityListView, TradeMessageView, MyTradeChatRoomListView, CreateTradeRoomView

urlpatterns = [
    path('active-rooms/', ActiveCommunityListView.as_view(), name='active-rooms'),
    path('my-activities/', MyActivityListView.as_view(), name='my-activities'),
    path('<str:isbn>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
    path('trade/<int:trade_id>/messages/', TradeMessageView.as_view(), name='trade-messages'),
    path('trade/rooms/', MyTradeChatRoomListView.as_view(), name='my-trade-rooms'),
    path('trade/create/<str:isbn>/', CreateTradeRoomView.as_view(), name='create-trade-room'),
]