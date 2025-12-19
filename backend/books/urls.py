from django.urls import path
from .views import BookActionView

urlpatterns = [
    path('<int:book_id>/action/<str:action>/', BookActionView.as_view(), name='book-action'),
]