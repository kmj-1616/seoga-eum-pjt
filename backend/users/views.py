import threading    # AI 추천 생성을 백그라운드에서 처리 
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

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