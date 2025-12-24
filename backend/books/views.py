from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
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

class BookPagination(PageNumberPagination):
    page_size = 100             # 한 페이지당 100권
    page_size_query_param = 'page_size' # 프론트에서 ?page_size= 로 조절 가능
    max_page_size = 200

# 도서 검색 및 목록 조회 
class BookListView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        category_id = request.query_params.get('category', None)
        sort = request.query_params.get('sort', 'popular')
        
        # [추가] 소장 여부 파라미터 가져오기
        owned = request.query_params.get('owned', None)

        # 1. 기본 쿼리셋
        books = Book.objects.all().select_related('category')

        # [추가] 2-1. 소장 중인 도서 필터링 로직
        if owned == 'true':
            if request.user.is_authenticated:
                # 현재 로그인한 유저가 소장한 책들만 필터링
                books = books.filter(owned_users=request.user)
            else:
                # 로그인 안 되어있으면 빈 목록 반환
                return Response({"results": [], "count": 0})

        # 2-2. 검색 필터링 (기존 코드)
        if query:
            books = books.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )

        # 3. 카테고리 필터링 (기존 코드)
        if category_id:
            books = books.filter(category_id=category_id)

        # 4. 정렬 (기존 코드)
        if sort == 'popular':
            books = books.order_by('-loan_count', '-id')
        elif sort == 'latest':
            books = books.order_by('-pub_year', '-id')

        # 5. 페이지네이션 적용
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        
        # [수정] 목록용 시리얼라이저에 context 추가 
        # (그래야 Serializer 안에서 request.user를 인식해 is_owned 필드를 채울 수 있습니다)
        serializer = BookListSerializer(result_page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

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
        query = self.request.query_params.get('q')

        if query:
            # 이름 혹은 주소에 검색어가 포함된 경우 모두 검색
            queryset = queryset.filter(
                Q(lib_name__icontains=query) | Q(address__icontains=query)
            )
        return queryset[:50]