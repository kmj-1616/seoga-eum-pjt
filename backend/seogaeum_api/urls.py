from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 회원 관리 API
    path('api/v1/users/', include('users.urls')),
    
    # 추후 추가될 API들
    # path('api/v1/books/', include('books.urls')),
    # path('api/v1/community/', include('community.urls')),
]