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

def clean_book_data(title, author):
    # 1. 제목 정제 (기존 로직 유지)
    clean_title = re.split(r'[:;=]', title)[0].strip()
    if not clean_title:
        clean_title = title.strip()

    # 2. 저자 정제 고도화
    # (1) 괄호와 그 안의 내용 모두 제거 (예: (지은이), [지음], (글) 등 삭제)
    # 
    clean_author = re.sub(r'[\(\[].*?[\)\]]', '', author).strip()
    
    # (2) 불필요한 접두어 및 수식어 제거 (글:, 그림:, 지은이: 등)
    clean_author = re.sub(r'^(지은이|원작|저자|글·그림|글|그림|저|원작|특대호 원고)[:\s]*', '', clean_author).strip()
    
    # (3) 구분자(세미콜론, 쉼표, 슬래시) 기준으로 자르기
    clean_author = re.split(r'[;,/]', clean_author)[0].strip()
    
    # (4) 남은 텍스트에서 불필요한 단어 제거 (글, 그림 등이 단독으로 남은 경우)
    clean_author = re.sub(r'\s*(지음|옮김|역|그림|글|글·|원작|엮음|그린이|옮긴이|감수|원고)$', '', clean_author).strip()

    # (5) 최종 예외 처리
    if not clean_author or len(clean_author) < 1:
        if author:
            # 정제 실패 시 원본에서 가장 앞의 단어라도 추출
            clean_author = re.sub(r'[\(\[].*?[\)\]]', '', author).split()[0].strip()
        else:
            clean_author = "저자 미상"
            
    return clean_title, clean_author

def get_detailed_info(isbn):
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    url = "http://data4library.kr/api/srchDtlList"
    params = {
        "authKey": auth_key, 
        "isbn13": isbn, 
        "loaninfoYN": "Y", 
        "format": "json"
    }
    
    result = {"description": "", "loan_count": 0}
    try:
        res = requests.get(url, params=params)
        response_json = res.json().get('response', {})
        
        # 1. 줄거리 추출
        detail = response_json.get('detail', [])
        if detail and isinstance(detail, list):
            result["description"] = detail[0].get('book', {}).get('description', "")
            
        # 2. 대출 건수 추출 
        loan_info_data = response_json.get('loanInfo', [])
        
        # loan_info_data가 리스트 형태이고 내용이 있을 때만 실행
        if isinstance(loan_info_data, list) and len(loan_info_data) > 0:
            total_info = loan_info_data[0].get('Total', {})
            # total_info가 dict가 아닐 경우를 대비해 한 번 더 체크
            if isinstance(total_info, dict):
                result["loan_count"] = int(total_info.get('loanCnt', 0))
                
    except Exception as e:
        print(f"⚠️ 데이터 파싱 건너뜀 ({isbn}): {e}")
    
    return result

def update_books_from_api(page_count=5):
    """인기 도서 목록을 가져와서 DB를 최신화 (줄거리 & 대출 건수 포함)"""
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    base_url = "http://data4library.kr/api/loanItemSrch"
    
    new_count = 0
    updated_count = 0
    
    print(f"🔄 총 {page_count}페이지 동기화 시작...")

    for page_no in range(1, page_count + 1):
        params = {"authKey": auth_key, "pageSize": 50, "pageNo": page_no, "format": "json"}
        try:
            response = requests.get(base_url, params=params)
            docs = response.json().get('response', {}).get('docs', [])
            
            for item in docs:
                book_info = item.get('doc', {})
                isbn = book_info.get('isbn13')
                if not isbn: continue

                # 1. 원본 데이터 가져오기
                raw_title = book_info.get('bookname', '')
                raw_author = book_info.get('authors', '')

                # 2. 정제 함수 호출 (제목의 부제와 저자의 불필요한 수식어 제거)
                title, author = clean_book_data(raw_title, raw_author)

                # 3. 상세 정보(줄거리 + 대출건수) 가져오기
                detailed_data = get_detailed_info(isbn)
                
                description = detailed_data["description"]
                if not description:
                    # 상세 줄거리가 없으면 원본의 짧은 줄거리라도 사용
                    description = book_info.get('description', f"{title}에 대한 상세 정보가 준비 중입니다.")
                
                loan_count = detailed_data["loan_count"]

                # 4. 카테고리 처리 
                class_nm = book_info.get('class_nm', '').strip()
                if not class_nm:
                    category_name = "기타"
                else:
                    category_name = class_nm.split('>')[0].strip()
                    if not category_name:
                        category_name = "기타"
                
                category_instance, _ = Category.objects.get_or_create(name=category_name)

                # 5. DB 저장 및 업데이트
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
                        'loan_count': loan_count, 
                    }
                )
                if created: new_count += 1
                else: updated_count += 1
                    
        except Exception as e:
            print(f"❌ {page_no}페이지 처리 중 오류: {e}")

    print(f"✅ 동기화 완료! (새로 추가: {new_count}, 갱신: {updated_count})")

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