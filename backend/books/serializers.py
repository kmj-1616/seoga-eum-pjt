from rest_framework import serializers
from .models import Book, Recommendation

# 1. 도서 목록용 (홈 화면)
class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover_url', 'category', 'loan_count']

# 2. 도서 상세용 (상세 페이지)
class BookSerializer(serializers.ModelSerializer):
    is_wish = serializers.SerializerMethodField()
    is_owned = serializers.SerializerMethodField()
    chat_count = serializers.IntegerField(source='messages.count', read_only=True)
    # AI 추천 사유 (DB에 저장된 정보를 가져옴)
    ai_recommendation_reason = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
                    'id', 'title', 'author', 'publisher', 'pub_year', 'isbn', 
                    'description', 'cover_url', 'category', 'loan_count',
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