from django.db import models
from django.conf import settings

class Book(models.Model):
    # 기본 도서 정보 (도서관정보나루 API 활용) 
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    pub_year = models.IntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField(null=True, blank=True)
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True) # 장르
    
    # 추천 및 활동 데이터
    loan_count = models.IntegerField(default=0) # 전체 대출 횟수
    
    # 사용자와의 관계: '함께 읽어요' 활동의 기반이 됨 
    wish_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='wish_books', blank=True
    ) # 구매/읽기 원해요
    owned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='owned_books', blank=True
    ) # 소장 중이에요

    def __str__(self):
        return self.title

# AI 기반 추천 기능을 위한 모델 
class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    # AI가 생성한 개인 맞춤형 추천 사유
    reason = models.TextField() 
    
    # 언제 생성된 추천인지 (최신성 유지 위함)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book') # 한 유저에게 한 책에 대한 추천은 하나만 저장