from django.urls import path
from .views import ChatMessageListCreateView, MyActivityListView, ActiveCommunityListView, TradeMessageView, MyTradeChatRoomListView, CreateTradeRoomView, TradeStatusRequestView, TradeStatusRequestApprovalView, TradeSellerApprovalView, BuyerReceiptCompleteView, TradeLocationUpdateView

urlpatterns = [
    path('active-rooms/', ActiveCommunityListView.as_view(), name='active-rooms'),
    path('my-activities/', MyActivityListView.as_view(), name='my-activities'),
    path('<str:isbn>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
    path('trade/<int:trade_id>/messages/', TradeMessageView.as_view(), name='trade-messages'),
    path('trade/rooms/', MyTradeChatRoomListView.as_view(), name='my-trade-rooms'),
    path('trade/create/<str:isbn>/', CreateTradeRoomView.as_view(), name='create-trade-room'),
    path('trade/<int:trade_id>/request-status/', TradeStatusRequestView.as_view(), name='request-status-change'),
    path('trade/<int:trade_id>/request/<int:request_id>/approve/', TradeStatusRequestApprovalView.as_view(), name='approve-status-change'),
    path('trade/<int:trade_id>/seller-approval/', TradeSellerApprovalView.as_view(), name='seller-approval'),
    path('trade/<int:trade_id>/buyer-receipt-complete/', BuyerReceiptCompleteView.as_view(), name='buyer-receipt-complete'),
    path('trade/<int:trade_id>/update-location/', TradeLocationUpdateView.as_view(), name='update-location'),
]