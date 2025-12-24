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
    
class TradeChatRoom(models.Model):
    # 어떤 도서 거래인지
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='trade_rooms')
    # 판매자(소장자)와 구매자(구매희망자)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sales_chats')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_chats')
    
    # 거래 상태 (프론트 tradeData.status와 연동)
    STATUS_CHOICES = [
        ('REQUESTED', '거래 요청'),
        ('LIBRARY_STORED', '도서관 보관 중'),
        ('COMPLETED', '거래 완료'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'seller', 'buyer')

class TradeMessage(models.Model):
    room = models.ForeignKey(TradeChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)