from rest_framework import serializers
from .models import Book, Recommendation, Category
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

# 3. 도서 상세용 (상세 페이지)
class BookSerializer(serializers.ModelSerializer):
    is_wish = serializers.SerializerMethodField()
    is_owned = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    # Community 앱의 ChatMessage 개수를 가져오는 필드
    chat_count = serializers.SerializerMethodField()
    ai_recommendation_reason = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'publisher', 'pub_year', 'isbn', 
            'description', 'cover_url', 'category', 'category_name', 'loan_count',
            'is_wish', 'is_owned', 'chat_count', 'ai_recommendation_reason'
        ]
    
    # 현재 로그인한 유저가 '읽고 싶어요'를 눌렀는지 확인
    def get_is_wish(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.wish_users.filter(pk=user.pk).exists()
        return False

    # 현재 로그인한 유저가 '소장 중'인지 확인
    def get_is_owned(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.owned_users.filter(pk=user.pk).exists()
        return False
    
    # ChatMessage 개수를 동적으로 계산하는 메서드
    def get_chat_count(self, obj):
        # obj(현재 Book 객체)에 연결된 ChatMessage의 개수를 반환
        return ChatMessage.objects.filter(book=obj).count()
    
    def get_ai_recommendation_reason(self, obj):
            user = self.context.get('request').user
            if user and user.is_authenticated:
                # 현재 책(obj)과 유저에 해당하는 추천 데이터를 DB에서 조회
                recommendation = Recommendation.objects.filter(user=user, book=obj).first()
                if recommendation:
                    return recommendation.reason
                return "사용자님의 취향을 분석 중입니다." # 데이터가 아직 없을 경우 대비
            return None
    
# 3. 도서관별 도서 소장여부 및 대출 가능여부 조회 (도서관정보나루 API용) 
class LibraryStatusSerializer(serializers.Serializer):
    libName = serializers.CharField()      # 도서관 이름
    hasBook = serializers.CharField()      # 소장 여부 (Y/N)
    loanAvailable = serializers.CharField() # 대출 가능 여부 (Y/N)