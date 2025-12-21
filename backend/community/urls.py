from django.urls import path
from .views import ChatMessageListCreateView

urlpatterns = [
    path('<str:isbn>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
]