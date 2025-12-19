# books/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Book

class BookActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, book_id, action):
        book = get_object_or_404(Book, id=book_id)
        user = request.user

        if action == 'wish':
            if book.wish_users.filter(id=user.id).exists():
                book.wish_users.remove(user)
                return Response({"message": "희망 도서에서 삭제되었습니다.", "is_wish": False})
            else:
                book.wish_users.add(user)
                return Response({"message": "희망 도서에 추가되었습니다.", "is_wish": True})
        
        elif action == 'owned':
            if book.owned_users.filter(id=user.id).exists():
                book.owned_users.remove(user)
                return Response({"message": "소장 도서에서 삭제되었습니다.", "is_owned": False})
            else:
                book.owned_users.add(user)
                return Response({"message": "소장 도서에 추가되었습니다.", "is_owned": True})
        
        return Response({"error": "잘못된 접근입니다."}, status=status.HTTP_400_BAD_REQUEST)