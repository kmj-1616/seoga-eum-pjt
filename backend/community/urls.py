from django.urls import path
from .views import ChatMessageListCreateView, MyActivityListView

urlpatterns = [
    path('my-activities/', MyActivityListView.as_view(), name='my-activities'),
    path('<str:isbn>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
]