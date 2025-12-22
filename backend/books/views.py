from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Book, Recommendation, Category, Library
from .serializers import RecommendationSerializer, BookSerializer, BookListSerializer, CategorySerializer, LibrarySerializer 
from .utils import generate_ai_recommendations

# 1. AI 추천 뷰 
class RecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # 최신 순으로 5개 가져오기
        recommendations = Recommendation.objects.filter(user=user).order_by('-created_at')[:5]
        
        # 1. 추천 데이터가 아예 없는 경우에만 실시간 생성 (force_update=False)
        if not recommendations.exists():
            success = generate_ai_recommendations(user, force_update=False)
            if success:
                recommendations = Recommendation.objects.filter(user=user).order_by('-created_at')[:5]
            else:
                return Response({"error": "AI 추천을 생성할 수 없습니다."}, status=500)
        
        # 2. 결과 반환 
        serializer = RecommendationSerializer(recommendations, many=True, context={'request': request})
        return Response(serializer.data)

# 2. 도서 액션 뷰 (희망도서/소장도서)
class BookActionView(APIView):

    def post(self, request, isbn, action):
        # 1. isbn으로 책 찾기 (없으면 404 에러)
        book = get_object_or_404(Book, isbn=isbn)
        user = request.user
        
        if not user.is_authenticated:
            return Response({"detail": "로그인이 필요한 서비스입니다."}, status=status.HTTP_401_UNAUTHORIZED)

        if action == 'wish':
            # 찜하기 로직: 이미 있다면 취소, 없다면 추가 (Toggle 방식)
            if book.wish_users.filter(pk=user.pk).exists():
                book.wish_users.remove(user)
                message = "읽고 싶은 도서에서 삭제되었습니다."
            else:
                book.wish_users.add(user)
                message = "읽고 싶은 도서에 추가되었습니다."
                
        elif action == 'owned':
            # 소장하기 로직
            if book.owned_users.filter(pk=user.pk).exists():
                book.owned_users.remove(user)
                message = "소장 도서에서 삭제되었습니다."
            else:
                book.owned_users.add(user)
                message = "소장 도서에 추가되었습니다."
        else:
            return Response({"detail": "잘못된 액션입니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": message}, status=status.HTTP_200_OK)

# 도서 검색 및 목록 조회 
class BookListView(APIView):

    def get(self, request):
        query = request.query_params.get('q', '')
        category_id = request.query_params.get('category', None)
        sort = request.query_params.get('sort', 'popular')

        # 1. 기본 쿼리셋
        books = Book.objects.all().select_related('category')

        # 2. 검색 필터링 (제목 또는 저자)
        if query:
            books = books.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )

        # 3. 카테고리 필터링
        if category_id:
            books = books.filter(category_id=category_id)

        # 4. 인기순/최신순 정렬 
        if sort == 'popular':
            books = books.order_by('-loan_count', '-id')
        elif sort == 'latest':
            books = books.order_by('-pub_year', '-id')

        # 목록용 시리얼라이저 사용 (홈/검색 결과 화면)
        serializer = BookListSerializer(books[:100], many=True)
        return Response(serializer.data)

# 도서 정보 상세 조회 
class BookDetailView(APIView):
    # 비로그인 유저도 접근할 수 있도록 권한 설정 추가
    permission_classes = [AllowAny]

    def get(self, request, isbn):
        try:
            # ISBN13 기준으로 도서 조회
            book = Book.objects.get(isbn=isbn)
            
            # 상세용 시리얼라이저 사용
            serializer = BookSerializer(book, context={'request': request})
            return Response(serializer.data)
            
        except Book.DoesNotExist:
            return Response(
                {"detail": "해당 도서 정보를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )

# 카테고리 목록 조회 (검색 필터용)
class CategoryListView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class LibraryListView(generics.ListAPIView):
    """전국 도서관 검색 및 목록 조회 API"""
    serializer_class = LibrarySerializer

    def get_queryset(self):
        queryset = Library.objects.all().order_by('lib_name')
        # q: 도서관명 검색, region: 지역 검색
        query = self.request.query_params.get('q')
        region = self.request.query_params.get('region')

        if query:
            queryset = queryset.filter(lib_name__icontains=query)
        if region:
            queryset = queryset.filter(address__contains=region)
            
        return queryset[:50] # 검색 결과는 상위 50개만 