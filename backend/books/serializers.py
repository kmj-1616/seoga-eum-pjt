from rest_framework import serializers
from .models import Book, Recommendation, Category, Library, UserBookStock 
from community.models import ChatMessage 

# 0. 카테고리 정보용
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# 1. 도서 목록용 (홈 화면 & 마이페이지 나의 서가)
class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    # 사용자가 등록한 희망 판매가
    price = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'cover_url', 
            'category', 'category_name', 'loan_count', 'price' # price 추가
        ]

    def get_price(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 중개 모델에서 현재 유저가 이 책에 대해 등록한 판매가 조회
            stock = UserBookStock.objects.filter(user=request.user, book=obj).first()
            if stock:
                return stock.selling_price
        return 0 # 등록된 가격이 없으면 0원

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
    libCode = serializers.CharField()
    libName = serializers.CharField(allow_null=True)       # 도서관 이름
    hasBook = serializers.CharField()       # 소장 여부 (Y/N)
    loanAvailable = serializers.CharField() # 대출 가능 여부 (Y/N)

# 5. 도서 상세용 (상세 페이지) 
class BookSerializer(serializers.ModelSerializer):
    is_wish = serializers.SerializerMethodField()
    is_owned = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    chat_count = serializers.SerializerMethodField()
    
    # 실시간 대출 가능 여부 필드 (관심도서관 + 주변도서관 합친 5개 정보)
    library_status = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'publisher', 'pub_year', 'isbn', 
            'description', 'cover_url', 'category', 'category_name', 'loan_count',
            'is_wish', 'is_owned', 'chat_count', 'library_status' 
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
    

    def get_library_status(self, obj):
        user = self.context.get('request').user
        
        # 1. 유저 위치 설정 (로그인 안 했거나 위치 정보 없으면 싸피 캠퍼스)
        u_lat = getattr(user, 'latitude', None) or 37.5012
        u_lon = getattr(user, 'longitude', None) or 127.0395
        
        # 2. 우선순위 1: 자주 이용하는 도서관 (관심 도서관)
        fav_libs = []
        fav_names = [] 
        
        if user and user.is_authenticated and user.favorite_libraries:
            fav_names = [n.strip() for n in user.favorite_libraries.split(',') if n.strip()]
            
            # lib_name으로 DB 조회
            fav_libs = list(Library.objects.filter(lib_name__in=fav_names))

        # 2. 부족한 만큼 주변 도서관 추가 (이미 찾은 관심 도서관은 제외)
        needed_count = 5 - len(fav_libs)
        nearby_libs = []
        if needed_count > 0:
            # 이미 찾은 관심 도서관의 코드를 제외 리스트로 만듦
            excluded_codes = [l.lib_code for l in fav_libs]
            
            all_other_libs = Library.objects.exclude(lib_code__in=excluded_codes)
            nearby_libs = sorted(
                all_other_libs,
                key=lambda l: (l.latitude - u_lat)**2 + (l.longitude - u_lon)**2
            )[:needed_count]

        # 3. 데이터 통합 및 실시간 조회
        final_lib_list = fav_libs + nearby_libs
        from .utils import get_library_full_status
        return get_library_full_status(obj.isbn, final_lib_list, u_lat, u_lon)