from django.db import models
from django.contrib import admin
from .models import Book, Category, Recommendation

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # 목록에서 보여줄 필드들
    list_display = ('title', 'author', 'category', 'isbn', 'pub_year')
    # 필터 옵션 (우측 사이드바)
    list_filter = ('category', 'publisher')
    # 검색 가능 필드
    search_fields = ('title', 'author', 'isbn')
    # 한 페이지에 보여줄 개수
    list_per_page = 20

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')