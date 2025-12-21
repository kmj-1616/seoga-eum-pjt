# 📚 서가이음(Seogaeum) API 명세서 (v1.2)

## 🌐 Base URL
`http://127.0.0.1:8000/api/v1`

---

## [1] 도서 서비스 (Books)
**Base URL:** `/books/`

### 1. 도서 목록 및 검색 (F01)
* **Endpoint:** `/`
* **Method:** `GET` 
* **Query Params:**
    * `q`: 검색어 (제목/저자)
    * `sort`: `popular` (대출순), `latest` (최신순)
    * `category`: 카테고리 ID (숫자)
* **Response Example:**
    ```json
    [
      { "isbn": "9788937473135", "title": "작별하지 않는다", "author": "한강", "cover_url": "...", "loan_count": 120 }
    ]
    ```

### 2. 도서 상세 정보 조회 (F05)
* **Endpoint:** `/{isbn}/`
* **Method:** `GET` 
* **Description:** 특정 도서의 상세 정보와 현재 로그인 유저의 찜/소장 여부를 함께 반환합니다.
* **Response Example:**
    ```json
    {
      "isbn": "9788937473135",
      "title": "작별하지 않는다",
      "is_wished": true, 
      "is_owned": false,
      "loan_count": 120,
      "description": "..."
    }
    ```

### 3. 도서 액션: 찜하기 / 소장하기 (F06)
* **Endpoint:** `/{isbn}/action/{action}/`
* **Method:** `POST` 
* **Auth:** **Token 필요**
* **Path Variable:** `action`에 `wish` 또는 `owned` 입력 (Toggle 방식)

### 4. AI 맞춤 도서 추천 (F04)
* **Endpoint:** `/recommendations/`
* **Method:** `GET` 
* **Auth:** **Token 필요**
* **Description:** 유저 취향 기반 AI 추천 데이터 5건 반환.

---

## [2] 사용자 서비스 (Users)
**Base URL:** `/users/`

### 1. 회원가입 (F02)
* **Endpoint:** `/register/`
* **Method:** `POST`
* **Body (JSON):**
    ```json
    {
        "email": "user@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "nickname": "서가이음",
        "favorite_libraries": "강남도서관,서초도서관",
        "age_group": "20s",
        "gender": "M",
        "preferred_genres": "소설,인문"
    }
    ```
* **Note:** 가입 성공 시 자동 로그인 처리되어 `tokens`(access, refresh)가 반환됩니다.

### 2. 로그인 (F03)
* **Endpoint:** `/login/`
* **Method:** `POST`
* **Success Response:** `user` 정보 및 `tokens` (access, refresh)

### 3. 로그아웃
* **Endpoint:** `/logout/`
* **Method:** `POST`
* **Body:** `{"refresh": "REFRESH_TOKEN_STRING"}`
* **Note:** 사용한 Refresh 토큰을 블랙리스트에 등록하여 무효화합니다.

### 4. 프로필 관리 (F04)
* **조회:** `GET` `/profile/` (인증 필요)
* **수정:** `PATCH` `/profile/update/` (인증 필요)
    * **Note:** 닉네임, 나이대, 장르 등 수정 가능 (Partial Update 지원)

---

## [3] 커뮤니티 서비스 (Community)
**Base URL:** `/community/`

### 1. 한 줄 평(메시지) 조회 및 작성
* **Endpoint:** `/{isbn}/messages/`
* **Method:** `GET` (목록 조회) / `POST` (작성)
* **인증(Auth):** 
    * **조회:** 누구나 가능 (Public)
    * **작성:** 로그인 유저만 가능 (Token 필요)
* **Request Body (작성 시):**
    ```json
    { "content": "이 책의 문체가 정말 매력적이네요!" }
    ```
* **Success Response (조회 시):**
    ```json
    [
        {
            "id": 1,
            "user_id": 5,
            "nickname": "책벌레",
            "content": "정말 추천합니다!",
            "created_at": "오전 10:30"
        }
    ]
    ```

---

## 💡 프론트엔드 개발 가이드
1. **인증 헤더:** 권한이 필요한 API 호출 시 헤더에 `Authorization: Bearer <Access_Token>`을 포함해야 합니다.
2. **자동 로그인:** 회원가입 성공 시에도 토큰이 발급되므로 바로 메인 페이지 진입이 가능합니다.
3. **데이터 포맷:** `favorite_libraries`와 `preferred_genres`는 쉼표(`,`)로 구분된 문자열로 통신합니다.
4. **에러 코드:** 
    * `401 Unauthorized`: 토큰 만료 또는 인증 실패
    * `404 Not Found`: 존재하지 않는 ISBN으로 요청 시
    * `400 Bad Request`: 필수 필드 누락 또는 유효하지 않은 데이터(비밀번호 불일치 등)