from django.db import models
from django.conf import settings
from books.models import Book

class ChatMessage(models.Model):
    # 어떤 책에 대한 대화인지
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='messages')
    # 누가 작성했는지
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 대화 내용
    content = models.TextField()
    # 작성 시간
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # 시간 순서대로 정렬 (채팅 메신저처럼)

    def __str__(self):
        return f'{self.user.nickname}: {self.content[:20]}'