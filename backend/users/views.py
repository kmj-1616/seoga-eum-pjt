import threading    # AI 추천 생성을 백그라운드에서 처리 
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from books.models import Book, UserBookStock

# books 앱의 utils에서 AI 추천 함수 임포트
from books.utils import generate_ai_recommendations

from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    UserUpdateSerializer
)

# 1. 회원가입 API (F02) 
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer   # 회원가입과 동시에 자동 로그인

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        update_last_login(None, user)

        # 회원가입 성공 후 백그라운드에서 AI 추천 생성
        threading.Thread(target=generate_ai_recommendations, args=(user, True)).start()

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': '회원가입이 완료되었습니다.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


# 2. 로그인 API (F03)
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': '이메일과 비밀번호를 모두 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 사용자 인증
        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # user가 존재하면 
        update_last_login(None, user) # last_login 기록
        refresh = RefreshToken.for_user(user) # 토큰 생성

        return Response({
            'message': '로그인 성공',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


# 3. 프로필 조회 API (F04 - 조회)
class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# 4. 프로필 수정 API (F04 - 수정)
class UserProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save() # 수정된 유저 객체 저장

            # 프로필 정보(나이, 성별, 선호장르 등)가 변경되었으므로 추천 강제 갱신
            threading.Thread(target=generate_ai_recommendations, args=(user, True)).start()

            return Response({
                'message': '프로필이 수정되었습니다.',
                'user': UserSerializer(user).data
            })


# 5. 로그아웃 API 
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # simplejwt의 blacklist 기능 사용 시
            return Response(
                {'message': '로그아웃 되었습니다.'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': '로그아웃 처리 중 오류가 발생했습니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
# 6. 가격 등록 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_price(request, isbn):
    # 1. 해당 도서가 DB에 있는지 확인
    book = get_object_or_404(Book, isbn=isbn)
    
    # 2. 유저와 도서의 소장 관계(중개 모델) 조회
    # 프론트에서 '소장 중이에요'를 먼저 눌러서 데이터가 생성된 상태여야 함
    stock = UserBookStock.objects.filter(user=request.user, book=book).first()
    
    if not stock:
        return Response(
            {'error': "먼저 '소장 중이에요' 버튼을 눌러 도서를 등록해 주세요."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 3. 가격 업데이트
    price = request.data.get('price')
    if price is None:
        return Response({'error': '가격을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
    stock.selling_price = price
    stock.save()
    
    return Response({
        'message': '서책의 가치가 등록되었습니다.',
        'selling_price': stock.selling_price
    }, status=status.HTTP_200_OK)


# 7. 소장 중인 이웃 목록 조회 API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_owners(request, isbn):
    """
    해당 책을 소장하고 가격을 등록한 이웃 목록 + 도서관 정보를 반환합니다.
    """
    try:
        # UserBookStock에서 해당 ISBN을 가진 데이터 조회 (유저 정보 포함)
        owners_stock = UserBookStock.objects.filter(
            book__isbn=isbn, 
            selling_price__gt=0
        ).select_related('user')
        
        results = []
        for s in owners_stock:
            results.append({
                'id': s.user.id,
                'nickname': s.user.nickname,
                'price': s.selling_price,
                # 유저 모델의 favorite_libraries 필드 추가
                'libraries': s.user.favorite_libraries 
            })
            
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)