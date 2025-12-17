from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 관리자 목록 화면 설정
    list_display = ('email', 'nickname', 'age_group', 'gender', 'is_staff')
    
    # 상세 정보 수정 화면 설정 (필드 그룹화)
    fieldsets = (
        ("계정 정보", {'fields': ('email', 'password')}),
        ('개인 프로필', {'fields': ('nickname', 'age_group', 'gender')}),
        ('이용 및 취향', {'fields': ('favorite_libraries', 'preferred_genres')}),
        ('권한 및 상태', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요 날짜', {'fields': ('last_login', 'date_joined')}),
    )

    # 유저 생성 화면 설정 (Add User)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password', 'age_group', 'gender', 'favorite_libraries', 'preferred_genres'),
        }),
    )

    search_fields = ('email', 'nickname')
    ordering = ('email',)