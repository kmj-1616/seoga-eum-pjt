from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Book(models.Model):
    # 기본 도서 정보
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    pub_year = models.IntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField(null=True, blank=True)
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    
    # 관계 설정
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    loan_count = models.IntegerField(default=0)
    
    # 구매 원해요 
    wish_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='wish_books', blank=True
    )
    
    # 소장 중이에요 (중개 모델 UserBookStock을 거쳐서 연결)
    owned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='UserBookStock', 
        related_name='owned_books', 
        blank=True
    )

    def __str__(self):
        return self.title

# 중개 모델 
class UserBookStock(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    # 추가 정보: 희망 판매가 (기본값 0원)
    selling_price = models.PositiveIntegerField(default=0, verbose_name="희망 판매가")
    
    # 소장 도서로 등록한 시간
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 유저가 같은 책을 여러 번 소장 등록하는 것 방지
        unique_together = ('user', 'book')
        verbose_name = "도서 소장 정보"

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

class Library(models.Model):
    lib_code = models.CharField(max_length=20, primary_key=True) # libCode
    lib_name = models.CharField(max_length=100) # libName
    address = models.CharField(max_length=255) # address
    tel = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    homepage = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.lib_name