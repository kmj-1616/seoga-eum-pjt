#!/bin/bash
cd "$(dirname "$0")"
echo "마이그레이션 생성 중..."
python manage.py makemigrations community
echo "마이그레이션 적용 중..."
python manage.py migrate
echo "완료!"
