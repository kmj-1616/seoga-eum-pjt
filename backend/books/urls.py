from django.urls import path
from .views import RecommendationView, BookActionView

urlpatterns = [
    path('recommendations/', RecommendationView.as_view(), name='recommendation_list'),
    path('<int:book_id>/action/<str:action>/', BookActionView.as_view(), name='book-action'),
]