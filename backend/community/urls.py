from django.urls import path
from .views import ChatMessageListCreateView

urlpatterns = [
    path('<int:book_id>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
]