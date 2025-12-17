from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# 1. 회원가입용 Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'nickname',
            'age_group', 'gender', 'favorite_libraries', 'preferred_genres'
        ]

    def validate(self, attrs):
        # 비밀번호 확인 검증
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def create(self, validated_data):
        # password_confirm 제거 (DB에 저장하지 않음)
        validated_data.pop('password_confirm')
        
        # User 생성 (set_password로 해싱)
        user = User.objects.create_user(**validated_data)
        return user


# 2. 로그인 응답/프로필 조회용 Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'nickname', 'age_group', 'gender',
            'favorite_libraries', 'preferred_genres', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'date_joined']


# 3. 프로필 수정용 Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'nickname', 'age_group', 'gender',
            'favorite_libraries', 'preferred_genres'
        ]

    def validate_nickname(self, value):
        # 닉네임 중복 체크 (본인 제외)
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value