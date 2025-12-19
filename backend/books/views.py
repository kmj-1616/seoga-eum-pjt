from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Recommendation
from .serializers import RecommendationSerializer
from .utils import generate_ai_recommendations

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. 해당 유저의 추천 데이터가 있는지 확인
        recommendations = Recommendation.objects.filter(user=user).order_by('-created_at')[:5]
        
        # 2. 만약 추천 데이터가 하나도 없다면? (처음 가입한 유저 등)
        if not recommendations.exists():
            # 즉시 AI 추천 생성 함수 실행
            success = generate_ai_recommendations(user)
            if success:
                # 생성 후 다시 조회
                recommendations = Recommendation.objects.filter(user=user).order_by('-created_at')[:5]
            else:
                return Response({"error": "AI 추천을 생성할 수 없습니다."}, status=500)
        
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)