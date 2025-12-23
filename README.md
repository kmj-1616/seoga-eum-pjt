# seoga-eum-pjt
# 📚 서가이음 (Seogaeum)
> **"당신과 책, 그리고 도서관을 잇는 가장 따뜻한 방법"**

서가이음은 개인의 독서 취향을 분석하여 AI 기반 맞춤 도서를 추천하고, 내 주변 도서관의 실시간 소장 및 대출 현황을 한눈에 확인하며, 독자들과 실시간으로 소통할 수 있는 **지능형 도서 커뮤니티 플랫폼**입니다.

---

## 🚀 주요 기능 (Key Features)

### 1. AI 기반 맞춤형 도서 추천 (AI Recommendation)
- **개인화 알고리즘**: 유저가 선호하는 다중 장르와 연령대 데이터를 바탕으로 AI가 최적의 도서 5권을 선정합니다.
- **감성 큐레이션**: 단순한 목록 나열이 아닌, "문명의 비밀을 파헤친다!"와 같이 책을 읽어야 할 이유를 담은 감성적인 추천 문구를 제공합니다.

### 2. 실시간 도서관 인프라 연동 (Library Status)
- **내 주변 도서관 찾기**: Geolocation API를 통해 사용자의 현재 위치에서 가장 가까운 도서관 정보를 제공합니다.
- **실시간 대출 현황**: 공공도서관 데이터와 연동하여 특정 도서의 소장 여부(`hasBook`) 및 대출 가능 여부(`loanAvailable`)를 실시간으로 확인합니다.
- **관심 도서관 우선 순위**: 내가 자주 가는 도서관을 등록하면 상세 페이지 상단에 우선적으로 정보를 노출합니다.

### 3. 실시간 한 줄 평 커뮤니티 (Live Community)
- **책별 오픈 채팅**: 도서별로 생성된 커뮤니티에서 다른 독자들과 실시간으로 감상을 나눌 수 있습니다.
- **스마트 날짜 구분**: 메시지 내역이 바뀔 때마다 날짜 구분선이 자동으로 생성되어 대화 흐름을 파악하기 쉽습니다.
- **사용자 친화적 UI**: 내 메시지와 상대방 메시지를 시각적으로 구분하며, 가독성 높은 한국어 시간 포맷(오전/오후)을 제공합니다.

### 4. 개인 맞춤형 프로필 관리 (User Profile)
- **취향 업데이트**: 선호 장르나 관심 도서관이 바뀌면 AI 추천 목록이 백그라운드에서 자동으로 즉시 갱신됩니다.
- **찜/소장 관리**: 관심 있는 책은 '찜'하고, 이미 읽은 책은 '소장'으로 분류하여 나만의 서재를 구축할 수 있습니다.

---

## 🛠 기술 스택 (Tech Stack)

### Backend
- **Framework**: Django REST Framework (DRF)
- **Database**: SQLite / PostgreSQL
- **Auth**: Simple JWT (JSON Web Token)

### Frontend
- **Framework**: Vue 3 (Composition API)
- **State Management**: Reactive State (ref, computed)
- **Styling**: CSS3 (Scoped, Custom Fonts)
- **HTTP Client**: Axios

---

## 🌐 API 엔드포인트 요약
- `GET /api/v1/books/`: 도서 검색 및 정렬
- `GET /api/v1/books/{isbn}/`: 도서 상세 및 실시간 도서관 현황
- `GET /api/v1/books/recommendations/`: AI 맞춤 추천 리스트
- `GET/POST /api/v1/community/{isbn}/messages/`: 실시간 커뮤니티 메시지

[상세 API 명세서 보기](./docs/API_SPEC.md)

---

## 💡 시작하기 (Getting Started)
1. **위치 권한 허용**: 위치 기반 서비스를 이용하려면 브라우저의 위치 정보 접근을 허용해 주세요.
2. **로그인**: 더 깊은 참여를 위해 계정을 생성하고 선호 장르를 등록해 보세요.
