from rest_framework import serializers
from .models import Book, Recommendation, Category, Library 
from community.models import ChatMessage 

# 0. 카테고리 정보용
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# 1. 도서 목록용 (홈 화면)
class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover_url', 'category', 'category_name', 'loan_count']

# 2. AI 추천 목록 전용 (홈 화면의 추천 섹션에서 사용)
class RecommendationSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'book', 'reason', 'created_at']

# 3. 도서관 목록 정보용 
class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ['lib_code', 'lib_name', 'address', 'tel', 'latitude', 'longitude', 'homepage'] 

# 4. 실시간 대출 현황용 (API 응답 규격)
class LibraryStatusSerializer(serializers.Serializer):
    libName = serializers.CharField(allow_null=True)       # 도서관 이름
    hasBook = serializers.CharField()       # 소장 여부 (Y/N)
    loanAvailable = serializers.CharField() # 대출 가능 여부 (Y/N)

# 5. 도서 상세용 (상세 페이지) 
class BookSerializer(serializers.ModelSerializer):
    is_wish = serializers.SerializerMethodField()
    is_owned = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    chat_count = serializers.SerializerMethodField()
    ai_recommendation_reason = serializers.SerializerMethodField()
    
    # 실시간 대출 가능 여부 필드 추가
    library_status = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'publisher', 'pub_year', 'isbn', 
            'description', 'cover_url', 'category', 'category_name', 'loan_count',
            'is_wish', 'is_owned', 'chat_count', 'ai_recommendation_reason',
            'library_status'
        ]
    
    def get_is_wish(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.wish_users.filter(pk=user.pk).exists()
        return False

    def get_is_owned(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.owned_users.filter(pk=user.pk).exists()
        return False
    
    def get_chat_count(self, obj):
        return ChatMessage.objects.filter(book=obj).count()
    
    def get_ai_recommendation_reason(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            recommendation = Recommendation.objects.filter(user=user, book=obj).first()
            if recommendation:
                return recommendation.reason
            return "사용자님의 취향을 분석 중입니다."
        return None

    # 실시간 데이터 가져오기 로직
    def get_library_status(self, obj):
        user = self.context.get('request').user
        # 유저가 로그인했고, 관심 도서관(favorite_libraries) 정보가 있을 때만 호출
        if user and user.is_authenticated and user.favorite_libraries:
            from .utils import get_realtime_library_status
            # 유저의 도서관 코드와 현재 책의 ISBN으로 조회
            status_data = get_realtime_library_status(obj.isbn, user.favorite_libraries)
            return LibraryStatusSerializer(status_data).data
        return None