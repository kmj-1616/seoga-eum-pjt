from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# 이메일을 로그인 ID로 사용하기 위한 커스텀 매니저 
class UserManager(BaseUserManager):
    # 일반 사용자 생성 로직 
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일 주소는 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # 관리자 생성 로직 
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # 기본 username 필드 대신 email을 ID로 사용
    username = None
    email = models.EmailField(unique=True, verbose_name="이메일")
    
    # 회원가입 시 입력받는 이름 (AbstractUser의 first_name, last_name 대신 name 사용 가능)
    nickname = models.CharField(max_length=50, verbose_name="이름")
    
    # 자주 이용하는 공공도서관 (다중 선택된 도서관들을 문자열로 저장)
    # 예: "서초구립반포도서관, 국립중앙도서관"
    favorite_libraries = models.TextField(blank=True, verbose_name="자주 이용하는 공공도서관")
    
    # 나이대 및 성별
    AGE_CHOICES = [
        ('10s', '10대'), ('20s', '20대'), ('30s', '30대'),
        ('40s', '40대'), ('50s', '50대'), ('60s+', '60대 이상'),
    ]
    age_group = models.CharField(max_length=10, choices=AGE_CHOICES, verbose_name="나이대")
    
    GENDER_CHOICES = [
        ('M', '남성'), ('F', '여성'), ('O', '기타'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="성별")
    
    # 선호 장르 (프론트에서 리스트를 보내면 백엔드에서 문자열로 합쳐서 저장)
    # 예: "소설,과학,예술"
    preferred_genres = models.TextField(blank=True, verbose_name="선호 장르")

    objects = UserManager()

    USERNAME_FIELD = 'email'  # 로그인 ID로 email 사용
    REQUIRED_FIELDS = ['nickname']  # superuser 생성 시 필수 입력 필드

    def __str__(self):
        return self.email