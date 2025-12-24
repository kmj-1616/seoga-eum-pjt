from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserProfileUpdateView,
    UserLogoutView,
)
from users import views as user_views

app_name = 'users'

urlpatterns = [
    # 회원가입 (F02)
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # 로그인 (F03)
    path('login/', UserLoginView.as_view(), name='login'),
    
    # 로그아웃
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # 프로필 조회 (F04)
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # 프로필 수정 (F04)
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),

    path('<str:isbn>/register_price/', user_views.register_price, name='register_price'),
    path('<str:isbn>/owners/', user_views.get_owners, name='get_owners'),
]