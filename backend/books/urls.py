from django.urls import path
from .views import RecommendationView, BookActionView, BookListView, BookDetailView, CategoryListView, LibraryListView
from users import views as user_views

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('recommendations/', RecommendationView.as_view(), name='recommendation_list'),
    path('libraries/', LibraryListView.as_view(), name='library-list'),
    path('<str:isbn>/', BookDetailView.as_view(), name='book-detail'),
    path('<str:isbn>/action/<str:action>/', BookActionView.as_view(), name='book-action'),
    path('<str:isbn>/register-price/', user_views.register_price, name='register_price'),
    path('<str:isbn>/owners/', user_views.get_owners, name='get_owners'),
]