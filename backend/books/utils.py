import json
import os
import requests
import xmltodict
import re
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q, Count
from django.db.models.functions import Cast
from django.db.models import FloatField
import math
from openai import OpenAI
from .models import Book, Category, Recommendation, Library
from community.models import ChatMessage

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

def get_popular_books_by_user(user):
    """사용자의 성별/연령대별 최근 3개월 인기 대출 도서 리스트 조회"""
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    url = "http://data4library.kr/api/loanItemSrch"
    
    # 1. 날짜 설정: 현재 날짜 기준 3개월 전부터 어제까지
    end_dt = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_dt = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # 2. 성별/연령대 매핑 (API 코드 명세 반영)
    gender_code = '0' if user.gender == 'M' else '1' if user.gender == 'F' else '2'
    age_map = {'10s': '14', '20s': '20', '30s': '30', '40s': '40', '50s': '50', '60s+': '60'}
    age_code = age_map.get(user.age_group, '20')

    params = {
        "authKey": auth_key,
        "startDt": start_dt,
        "endDt": end_dt,
        "gender": gender_code,
        "age": age_code,
        "pageSize": 10,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params)
        docs = response.json().get('response', {}).get('docs', [])
        # API 응답에서 도서명(bookname) 리스트 추출
        return [d.get('doc', {}).get('bookname') for d in docs]
    except:
        return []

def generate_ai_recommendations(user, force_update=False):
    """사용자 프로필 + 실시간 인기 통계 + 커뮤니티 활동 기반 AI 추천 생성"""

    # 이미 추천 데이터가 있고 강제 업데이트가 아니면 그냥 리턴
    if not force_update and Recommendation.objects.filter(user=user).exists():
        return True
    
    if not settings.OPENAI_API_KEY: return False
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1")

    # 1. 커뮤니티 활동 분석 (댓글 5개 이상 시 카테고리 추출)
    user_comments = ChatMessage.objects.filter(user=user).select_related('book__category')
    active_interests = ""
    if user_comments.count() >= 5:
        top_cats = user_comments.values('book__category__name').annotate(c=Count('book__category')).order_by('-c')[:2]
        active_interests = f"최근 관심 카테고리: {', '.join([c['book__category__name'] for c in top_cats])}"

    # 2. 도서관 인기 대출 통계 확보 (최근 3개월 데이터)
    stat_popular_books = get_popular_books_by_user(user)
    stat_context = f"현재 해당 연령대/성별 인기 도서: {', '.join(stat_popular_books)}"

    # 3. 추천 후보 도서 추출 (다중 장르 대응)
    genres = [g.strip() for g in user.preferred_genres.split(',') if g.strip()]
    
    query = Q()
    for genre in genres:
        query |= Q(category__name__icontains=genre)
    
    # 선호 장르가 없거나 검색 결과가 없을 경우를 대비해 베스트셀러/소설 등 기본 후보 확보
    candidate_books = Book.objects.filter(query).order_by('?')[:30]
    
    if not candidate_books.exists():
        candidate_books = Book.objects.all().order_by('-loan_count')[:30]

    book_list_str = "\n".join([
        f"- ID:{b.id} | 제목:{b.title} | 카테고리:{b.category.name} | 줄거리:{b.description[:100]}" 
        for b in candidate_books
    ])

    # 4. 고도화된 프롬프트 구성
    prompt = f"""
    사용자 정보: {user.get_age_group_display()} {user.get_gender_display()}, 선호: {user.preferred_genres}
    활동 분석: {active_interests if active_interests else "신규 유저"}
    외부 통계: {stat_context}
    
    위 목록 중 유저에게 어울리는 5권을 선정해줘. 
    조건:
    1. 사용자의 여러 선호 카테고리가 골고루 포함되게 할 것.
    2. 이유는 도서의 줄거리 기반으로 30자 이내로 작성하고, 영화 포스터 카피처럼 강렬한 느낌표 문장으로 작성할 것.
    3. 반드시 아래 JSON 형식으로만 출력할 것. 다른 설명은 생략할 것.
    [도서 목록]
    {book_list_str}
    
    반드시 순수 JSON 형식으로만 응답할 것: [{{ "book_id": ID, "reason": "이유" }}]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "developer", "content": "당신은 트렌디한 감각을 가진 전문 사서입니다."}, {"role": "user", "content": prompt}],
            temperature=0.8
        )
        content = response.choices[0].message.content.strip()
        # 마크다운 태그 제거 로직
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        
        recommendations = json.loads(content)
        
        # 5. DB 업데이트 (트랜잭션 권장)
        from django.db import transaction
        with transaction.atomic():
            Recommendation.objects.filter(user=user).delete()
            for rec in recommendations[:5]: # 최대 5개 제한
                book = Book.objects.filter(id=rec.get('book_id')).first()
                if book:
                    Recommendation.objects.create(
                        user=user, 
                        book=book, 
                        reason=rec.get('reason')
                    )
        return True
    except Exception as e:
        print(f"❌ AI 오류: {e}")
        return False

    
def import_all_data():
    """books.json 파일에서 카테고리, 도서관, 도서를 순차적으로 임포트"""
    
    path = os.path.join(settings.BASE_DIR, 'fixtures', 'books.json')
    
    if not os.path.exists(path):
        print(f"❌ 파일을 찾을 수 없습니다: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 카테고리(Category) 임포트
    cat_count = 0
    for item in data:
        if item.get('model') == 'books.category':
            fields = item['fields']
            Category.objects.update_or_create(
                id=item['pk'],
                defaults={'name': fields.get('name')}
            )
            cat_count += 1
    print(f"✅ 카테고리 임포트 완료: {cat_count}개")

    # 2. 도서관(Library) 임포트
    lib_count = 0
    for item in data:
        if item.get('model') == 'books.library':
            fields = item['fields']
            Library.objects.update_or_create(
                lib_code=item['pk'],
                defaults={
                    'lib_name': fields.get('lib_name'),
                    'address': fields.get('address'),
                    'tel': fields.get('tel'),
                    'latitude': fields.get('latitude'),
                    'longitude': fields.get('longitude'),
                    'homepage': fields.get('homepage'),
                }
            )
            lib_count += 1
    print(f"✅ 도서관 임포트 완료: {lib_count}개")

    # 3. 도서(Book) 임포트
    book_count = 0
    for item in data:
        if item.get('model') == 'books.book':
            fields = item['fields']
            
            category_instance = Category.objects.filter(id=fields.get('category')).first()
            
            # pub_year 정제
            pub_year = fields.get('pub_year')
            if not pub_year and fields.get('pub_date'):
                try:
                    pub_year = int(str(fields.get('pub_date'))[:4])
                except:
                    pub_year = None

            Book.objects.update_or_create(
                isbn=fields.get('isbn'),
                defaults={
                    'title': fields.get('title'),
                    'author': fields.get('author'),
                    'publisher': fields.get('publisher'),
                    'description': fields.get('description'),
                    'cover_url': fields.get('cover_url') or fields.get('cover'),
                    'category': category_instance,
                    'pub_year': pub_year,
                    'loan_count': fields.get('loan_count', 0),
                }
            )
            book_count += 1
    print(f"✅ 도서 임포트 완료: {book_count}개")

# 도서관 목록 업데이트 
def update_libraries():
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    base_url = "http://data4library.kr/api/libSrch"
    regions = ["11", "31", "22", "21", "23", "24", "25", "26", "32", "33", "34", "35", "36", "37", "38", "39"]
    total_count = 0

    for region_code in regions:
        params = {"authKey": auth_key, "region": region_code, "pageSize": 100, "format": "json"}
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            libs_list = data.get('response', {}).get('libs', [])
            for item in libs_list:
                lib_info = item.get('lib', {})
                Library.objects.update_or_create(
                    lib_code=lib_info.get('libCode'),
                    defaults={
                        'lib_name': lib_info.get('libName'),
                        'address': lib_info.get('address'),
                        'tel': lib_info.get('tel'),
                        'latitude': float(lib_info.get('latitude')) if lib_info.get('latitude') else None,
                        'longitude': float(lib_info.get('longitude')) if lib_info.get('longitude') else None,
                        'homepage': lib_info.get('homepage'),
                    }
                )
                total_count += 1
        except Exception as e:
            print(f"Error region {region_code}: {e}")
    print(f"✅ {total_count}개 도서관 저장 완료")

# 사용자 위치 정보 기본값 
DEFAULT_LAT = 37.5012
DEFAULT_LON = 127.0395

def calculate_distance(lat1, lon1, lat2, lon2):
    """두 지점 사이의 직선 거리를 km로 계산 (Haversine 공식)"""
    if None in [lat1, lon1, lat2, lon2]:
        return 0
    radius = 6371  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(radius * c, 2)

def get_library_full_status(isbn, libraries, user_lat, user_lon):
    """
    도서관 객체 리스트를 받아 실시간 상태 및 거리 정보를 포함한 데이터 반환
    이 함수가 기존의 get_realtime_library_status를 대체합니다.
    """
    auth_key = getattr(settings, 'LIBRARY_API_KEY', None)
    url = "http://data4library.kr/api/bookExist"
    results = []

    for lib in libraries:
        # 실시간 API 호출 (소장 여부 확인)
        params = {
            "authKey": auth_key,
            "libCode": lib.lib_code,
            "isbn13": isbn,
            "format": "json"
        }
        
        has_book = "N"
        loan_available = "N"
        
        try:
            # 타임아웃을 짧게 설정하여 상세페이지 로딩 지연 방지
            resp = requests.get(url, params=params, timeout=1.5).json()
            exist_res = resp.get('response', {}).get('result', {})
            has_book = exist_res.get('hasBook', 'N')
            loan_available = exist_res.get('loanAvailable', 'N')
        except:
            pass # 실패 시 기본값 N 유지

        results.append({
            "libCode": lib.lib_code,
            "libName": lib.lib_name,
            "address": lib.address,
            "tel": lib.tel,
            "homepage": lib.homepage,
            "hasBook": has_book,
            "loanAvailable": loan_available,
            "distance": calculate_distance(user_lat, user_lon, lib.latitude, lib.longitude)
        })
    return results

def get_nearby_libraries_list(user_lat, user_lon, exclude_codes, limit=5):
    """
    관심 도서관을 제외한 주변 도서관 객체 리스트 반환
    """
    # 관심 도서관 제외하고 필터링
    all_other_libs = Library.objects.exclude(lib_code__in=exclude_codes)
    
    # 거리순 정렬 (단순 위경도 차이의 제곱합 사용 - 정렬용으로는 충분)
    nearby_libs = sorted(
        all_other_libs,
        key=lambda l: (l.latitude - user_lat)**2 + (l.longitude - user_lon)**2
    )
    
    return nearby_libs[:limit]