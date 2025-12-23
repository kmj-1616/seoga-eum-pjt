import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# .env 파일 로드 
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-xmhcg^l2z@_fbk%-^q=1cig1ca$&3$fc(s+79r$a2e&vwo12$e"
DEBUG = True

# API 키 
LIBRARY_API_KEY = os.getenv("LIBRARY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt", 
    "rest_framework_simplejwt.token_blacklist", 
    "books",
    "community",
    "users",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", 
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "seogaeum_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "seogaeum_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"

AUTH_USER_MODEL = 'users.User'

# CORS 설정 
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

SIMPLE_JWT = {
    # 1. Access Token: 실제 인증에 사용 (짧게 유지)
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=3), # 개발 편의를 위해 3시간으로 설정
    
    # 2. Refresh Token: Access Token을 재발급받을 때 사용 (길게 유지)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    # 3. 토큰 회전 (Rotate): Refresh Token을 사용해 Access를 갱신할 때마다 
    # 새로운 Refresh Token도 함께 발급할지 여부 (보안 강화)
    'ROTATE_REFRESH_TOKENS': True,
    
    # 4. 블랙리스트 (Blacklist): 로그아웃된 토큰을 다시 사용하지 못하게 기록
    'BLACKLIST_AFTER_ROTATION': True,
    
    # 5. 인증 헤더 설정
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
]