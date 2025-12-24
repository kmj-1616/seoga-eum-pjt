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
        ('APPROVED', '거래 승인'),
        ('LIBRARY_STORED', '도서관 보관 중'),
        ('COMPLETED', '거래 완료'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')

        # 거래 장소 및 보관함 정보 (판매자가 설정)
    location = models.CharField(max_length=255, blank=True, null=True, help_text="거래 장소")
    locker_number = models.CharField(max_length=50, blank=True, null=True, help_text="도서 보관함 번호")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'seller', 'buyer')

class TradeMessage(models.Model):
    room = models.ForeignKey(TradeChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TradeStatusRequest(models.Model):
    """거래 상태 변경 요청을 관리하는 모델"""
    room = models.ForeignKey(TradeChatRoom, on_delete=models.CASCADE, related_name='status_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_trade_requests')
    
    # 변경할 상태
    NEW_STATUS_CHOICES = [
        ('LIBRARY_STORED', '도서관 보관 중'),
        ('COMPLETED', '거래 완료'),
    ]
    new_status = models.CharField(max_length=20, choices=NEW_STATUS_CHOICES)
    
    # 요청 상태
    REQUEST_STATUS_CHOICES = [
        ('PENDING', '대기 중'),
        ('ACCEPTED', '수락됨'),
        ('REJECTED', '거절됨'),
    ]
    request_status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('room', 'new_status')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.room.id}: {self.requester.nickname} -> {self.get_new_status_display()}"