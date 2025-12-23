from django.urls import path
from .views import RecommendationView, BookActionView, BookListView, BookDetailView, CategoryListView, LibraryListView

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('recommendations/', RecommendationView.as_view(), name='recommendation_list'),
    path('libraries/', LibraryListView.as_view(), name='library-list'),
    path('<str:isbn>/', BookDetailView.as_view(), name='book-detail'),
    path('<str:isbn>/action/<str:action>/', BookActionView.as_view(), name='book-action'),
]