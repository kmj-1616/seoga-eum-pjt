import json
import os
import requests
import xmltodict
from django.conf import settings
from .models import Book, Category

def fetch_books_from_api(api_type="loanItemSrch"):
    """도서관정보나루 API 호출 함수"""
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    if not auth_key:
        return {"response": {"docs": []}} # 빈 결과 반환

    url = f"http://data4library.kr/api/{api_type}"
    params = {"authKey": auth_key, "pageSize": 50, "format": "json"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            return json.loads(json.dumps(xmltodict.parse(response.content)))
    except Exception as e:
        print(f"API 에러: {e}")
    return None

def import_all_data():
    """categories.json과 books.json 데이터를 통합 임포트"""
    
    # 1. 카테고리 임포트
    cat_path = os.path.join(settings.BASE_DIR, 'fixtures', 'categories.json')
    try:
        with open(cat_path, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
            for cat in categories_data:
                Category.objects.get_or_create(
                    id=cat['pk'],
                    defaults={'name': cat['fields']['name']}
                )
        print("카테고리 데이터 임포트 완료")
    except FileNotFoundError:
        print("categories.json 파일을 찾을 수 없습니다.")

    # 2. 도서 데이터 임포트
    book_path = os.path.join(settings.BASE_DIR, 'fixtures', 'books.json')
    try:
        with open(book_path, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
            
        new_books_count = 0
        for item in books_data:
            fields = item['fields']
            
            # 카테고리 연결
            cat_id = fields.get('category')
            category_instance = Category.objects.filter(id=cat_id).first()
            
            # 날짜 처리
            pub_year = None
            raw_date = fields.get('pub_date')
            if raw_date and len(raw_date) >= 4:
                try:
                    pub_year = int(raw_date[:4])
                except ValueError:
                    pass

            # 데이터 저장
            book, created = Book.objects.get_or_create(
                isbn=fields.get('isbn'),
                defaults={
                    'title': fields.get('title'),
                    'author': fields.get('author'),
                    'publisher': fields.get('publisher'),
                    'description': fields.get('description'),
                    'cover_url': fields.get('cover'),
                    'category': category_instance,
                    'pub_year': pub_year,
                }
            )
            if created:
                new_books_count += 1
        
        print(f"도서 데이터 임포트 완료 (새로 추가: {new_books_count}개)")
    except FileNotFoundError:
        print("books.json 파일을 찾을 수 없습니다.")