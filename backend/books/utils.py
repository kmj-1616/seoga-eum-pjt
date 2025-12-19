import json
import os
import requests
import xmltodict
import re
from django.conf import settings
from openai import OpenAI
from .models import Book, Category, Recommendation

def fetch_books_from_api(api_type="loanItemSrch"):
    """도서관정보나루 API 호출 도구"""
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    if not auth_key:
        return {"response": {"docs": []}} 

    url = f"http://data4library.kr/api/{api_type}"
    params = {"authKey": auth_key, "pageSize": 50, "format": "json"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            return json.loads(json.dumps(xmltodict.parse(response.content)))
    except Exception as e:
        print(f"⚠️ API 호출 에러: {e}")
    return None

def clean_text(text):
    """저자명 등에서 불필요한 문구를 제거"""
    if not text: return ""
    # '지은이:', '저자:' 등을 제거하고 앞뒤 공백 정리
    text = re.sub(r'^(지은이|저자|글|그림|옮긴이)\s*[:：]\s*', '', text)
    return text.strip()

def get_detailed_description(isbn):
    """상세 조회 API를 통해 누락된 줄거리 보강"""
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    url = "http://data4library.kr/api/srchDtlList"
    params = {"authKey": auth_key, "isbn13": isbn, "format": "json"}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        # API 응답 구조에 따라 안전하게 추출
        detail = data.get('response', {}).get('detail', [])
        if detail:
            return detail[0].get('book', {}).get('description', "")
    except:
        pass
    return ""

def update_books_from_api(page_count=5):
    """인기 도서 목록을 가져와서 DB를 최신화 (줄거리 보강 포함)"""
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    base_url = "http://data4library.kr/api/loanItemSrch"
    
    new_count = 0
    updated_count = 0
    
    print(f"🔄 총 {page_count}페이지에 걸쳐 데이터 동기화를 시작합니다...")

    for page_no in range(1, page_count + 1):
        params = {"authKey": auth_key, "pageSize": 50, "pageNo": page_no, "format": "json"}
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            for item in docs:
                book_info = item.get('doc', {})
                isbn = book_info.get('isbn13')
                if not isbn: continue

                # 저자명 정제 및 제목 가져오기
                author = clean_text(book_info.get('authors', ''))
                title = book_info.get('bookname', '')

                # 줄거리 확인 및 보강
                description = book_info.get('description', '').strip()
                if not description:
                    description = get_detailed_description(isbn)
                
                if not description:
                    description = f"{title}에 대한 상세 정보가 준비 중입니다."

                # 카테고리 처리
                category_raw = book_info.get('class_nm', '기타').split('>')[0].strip()
                category_instance, _ = Category.objects.get_or_create(name=category_raw)

                # DB 저장 (isbn을 기준으로 중복 방지)
                book, created = Book.objects.update_or_create(
                    isbn=isbn,
                    defaults={
                        'title': title,
                        'author': author,
                        'publisher': book_info.get('publisher'),
                        'description': description,
                        'cover_url': book_info.get('bookImageURL'),
                        'category': category_instance,
                        'pub_year': int(str(book_info.get('publication_year'))[:4]) if book_info.get('publication_year') else None,
                    }
                )
                if created:
                    new_count += 1
                else:
                    updated_count += 1
                    
        except Exception as e:
            print(f"❌ {page_no}페이지 처리 중 오류 발생: {e}")

    print("-" * 40)
    print(f"✅ 데이터 동기화가 성공적으로 완료되었습니다!")
    print(f"✨ 새로 추가된 도서: {new_count}권")
    print(f"🔄 정보가 갱신된 도서: {updated_count}권")
    print("-" * 40)

# def import_all_data():
#     """categories.json과 books.json 데이터를 통합 임포트"""
#     # 1. 카테고리 임포트
#     cat_path = os.path.join(settings.BASE_DIR, 'fixtures', 'categories.json')
#     try:
#         with open(cat_path, 'r', encoding='utf-8') as f:
#             categories_data = json.load(f)
#             for cat in categories_data:
#                 Category.objects.get_or_create(
#                     id=cat['pk'],
#                     defaults={'name': cat['fields']['name']}
#                 )
#         print("✅ 카테고리 데이터 임포트 완료")
#     except FileNotFoundError:
#         print("❌ categories.json 파일을 찾을 수 없습니다.")

#     # 2. 도서 데이터 임포트
#     book_path = os.path.join(settings.BASE_DIR, 'fixtures', 'books.json')
#     try:
#         with open(book_path, 'r', encoding='utf-8') as f:
#             books_data = json.load(f)
            
#         new_books_count = 0
#         for item in books_data:
#             fields = item['fields']
#             category_instance = Category.objects.filter(id=fields.get('category')).first()
            
#             pub_year = None
#             raw_date = fields.get('pub_date')
#             if raw_date and len(raw_date) >= 4:
#                 try:
#                     pub_year = int(raw_date[:4])
#                 except ValueError:
#                     pass

#             book, created = Book.objects.get_or_create(
#                 isbn=fields.get('isbn'),
#                 defaults={
#                     'title': fields.get('title'),
#                     'author': fields.get('author'),
#                     'publisher': fields.get('publisher'),
#                     'description': fields.get('description'),
#                     'cover_url': fields.get('cover'),
#                     'category': category_instance,
#                     'pub_year': pub_year,
#                 }
#             )
#             if created:
#                 new_books_count += 1
#         print(f"✅ 도서 데이터 임포트 완료 (새로 추가: {new_books_count}개)")
#     except FileNotFoundError:
#         print("❌ books.json 파일을 찾을 수 없습니다.")

def generate_ai_recommendations(user):
    """SSAFY GMS 최종 가이드에 맞춘 AI 추천 함수 (데이터 퀄리티 보강)"""
    
    if not settings.OPENAI_API_KEY:
        return False

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1"
    )

    user_pref_str = user.preferred_genres if user.preferred_genres else "전체"
    user_info = f"{user.get_age_group_display()} {user.get_gender_display()}" 
    
    first_genre = user_pref_str.split(',')[0].strip()
    candidate_books = Book.objects.filter(category__name__icontains=first_genre).order_by('?')[:20]
    
    if not candidate_books.exists():
        candidate_books = Book.objects.order_by('?')[:20]

    book_list_str = "\n".join([
        f"- ID: {b.id} | 제목: {b.title} | 저자: {b.author} | 줄거리: {b.description[:150]}..." 
        for b in candidate_books
    ])

    prompt = f"""
    사용자 정보: {user_info}, 선호 장르: {user_pref_str}
    위 사용자의 취향에 맞춰 아래 도서 목록 중 가장 잘 어울리는 책 5권을 선정해줘.
    [도서 목록]
    {book_list_str}
    
    형식은 반드시 순수 JSON만 보내줘. 
    [
        {{"book_id": 책ID, "reason": "줄거리를 참고한 구체적인 추천 이유"}}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "developer", "content": "You are a helpful book recommendation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        recommendations = json.loads(content)
        
        for rec in recommendations:
            try:
                book = Book.objects.get(id=rec['book_id'])
                Recommendation.objects.update_or_create(
                    user=user,
                    book=book,
                    defaults={'reason': rec['reason']}
                )
            except Book.DoesNotExist:
                continue
        
        return True

    except Exception as e:
        print(f"❌ AI 추천 생성 중 오류: {e}")
        return False