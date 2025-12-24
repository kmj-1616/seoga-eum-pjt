<template>
  <div v-if="book" class="detail-outer-container"> <div class="detail-container">
      <aside class="side-panel">
        <div class="cover-card">
          <img :src="book.cover_url" alt="Book Cover" class="book-cover" />
        </div>
        
        <div class="action-buttons">
          <router-link :to="`/community/${book.isbn}`" class="btn-classic btn-chat">
            <i class="icon">💬</i> 함께 읽어요
          </router-link>
          
          <button @click="toggleAction('owned')" :class="['btn-classic', 'btn-owned', { active: book.is_owned }]">
            <i class="icon">{{ book.is_owned ? '✅' : '📚' }}</i> 소장 중이에요
          </button>

          <button @click="toggleAction('wish')" :class="['btn-classic', 'btn-wish', { active: book.is_wish }]">
            <i class="icon">{{ book.is_wish ? '❤️' : '🤍' }}</i> 구매 원해요
          </button>
        </div>
      </aside>

      <main class="main-content">
        <section class="info-card">
          <div class="info-header">
            <span class="category-tag"># {{ book.category_name }}</span>
            <h1 class="book-title">{{ book.title }}</h1>
            <h2 class="book-author">{{ book.author }}</h2>
          </div>

          <div class="info-grid">
            <div class="info-item"><strong>출판사</strong> {{ book.publisher }}</div>
            <div class="info-item"><strong>출판년도</strong> {{ book.pub_year }}</div>
            <div class="info-item"><strong>ISBN</strong> {{ book.isbn }}</div>
            <div class="info-item"><strong>최근 3개월 대출 건수</strong> <span class="highlight">{{ book.loan_count.toLocaleString() }}회</span></div>
          </div>
          
          <div class="book-description">
            <p>{{ book.description }}</p>
          </div>
        </section>

        <section class="library-card">
          <div class="section-header-classic">
            <span class="decoration-line"></span>
            <h3 class="section-title">내 주변 및 관심 도서관 현황</h3>
            <span class="decoration-line"></span>
          </div>
          
          <div class="library-list">
            <div v-for="lib in book.library_status" :key="lib.libCode" class="lib-item">
              <div class="lib-header">
                <span class="lib-name">{{ lib.libName }}</span>
                <span class="lib-distance">{{ lib.distance }}km</span>
              </div>
              
              <div class="lib-footer">
                <span :class="['status-badge', lib.loanAvailable === 'Y' ? 'available' : 'unavailable']">
                  {{ lib.loanAvailable === 'Y' ? '✓ 대출 가능' : '✗ 대출 불가' }}
                </span>
                <a :href="lib.homepage" target="_blank" class="lib-link">도서관 상세 보기</a>
              </div>
            </div>
            <p class="library-disclaimer">
              ※ 대출 가능 여부는 조회일 기준 전날 자료로 제공됩니다. 실시간 현황은 도서관 홈페이지를 확인해 주십시오.
            </p>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const book = ref(null)

const fetchBookDetail = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const headers = {}
    if (token && token !== 'null') headers.Authorization = `Bearer ${token}`

    // 1. localStorage에서 저장된 위치 정보 가져오기
    // 로그인 시 저장하지 않았을 경우를 대비해 null 처리
    const lat = localStorage.getItem('user_lat')
    const lon = localStorage.getItem('user_lon')

    // 2. API 호출 시 params에 위치 정보 실어 보내기
    // 백엔드 utils.py의 get_library_full_status에서 user_lat, user_lon으로 활용됩니다.
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/books/${route.params.isbn}/`, { 
      headers,
      params: { 
        lat: lat, 
        lon: lon 
      }
    })
    
    book.value = response.data
  } catch (err) {
    console.error("데이터 로드 실패:", err)
  }
}

const toggleAction = async (actionType) => {
  const token = localStorage.getItem('access_token')
  
  // 1. 비로그인 상태 체크
  if (!token || token === 'null') {
    if (confirm("신분 확인이 필요한 서비스입니다. 페이지로 이동하시겠습니까?")) {
      router.push({ 
        path: '/login', 
        query: { redirect: route.fullPath } 
      })
    }
    return; 
  }

  // 2. 로그인 된 상태일 때만 실행되는 로직
  try {
    const response = await axios.post(`http://127.0.0.1:8000/api/v1/books/${book.value.isbn}/action/${actionType}/`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (actionType === 'wish') book.value.is_wish = !book.value.is_wish
    else if (actionType === 'owned') book.value.is_owned = !book.value.is_owned
    
    // alert(response.data.message) 
  } catch (err) {
    console.error("액션 실패:", err)
    if (err.response && err.response.status === 401) {
      alert("세션이 만료되었습니다. 다시 로그인해주세요.")
      router.push('/login')
    }
  }
} 

onMounted(fetchBookDetail)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');

/* 전체 배경 설정 */
.detail-outer-container {
  background-color: #fdfaf5;
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png');
  min-height: 100vh;
  padding: 40px 0;
  font-family: 'Hahmlet', serif;
}

.detail-container {
  display: flex;
  gap: 40px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 사이드 패널 */
.side-panel { flex: 0 0 300px; }

.cover-card {
  background: white;
  padding: 12px;
  border: 1px solid #d1b894;
  box-shadow: 10px 10px 20px rgba(0,0,0,0.05);
  margin-bottom: 25px;
}

.book-cover { width: 100%; display: block; }

/* 액션 버튼: 모든 버튼 너비를 100%로 통일 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-classic {
  width: 100%; /* 너비 일치 */
  box-sizing: border-box; /* 패딩 포함 너비 계산 */
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #81532e;
  font-family: 'Hahmlet', serif;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 16px;
  text-decoration: none;
}

.btn-chat { background: #81532e; color: #fdfaf5; }
.btn-chat:hover { background: #4a3423; }

.btn-owned, .btn-wish { background: white; color: #81532e; }
.btn-owned.active { background: #f5ece0; border-width: 2px; }
.btn-wish.active { background: #fff0f0; border-color: #ef4444; color: #ef4444; }

/* 메인 콘텐츠 */
.main-content { flex: 1; display: flex; flex-direction: column; gap: 25px; }

.info-card, .library-card {
  background: white;
  padding: 35px;
  border: 1px solid #d1b894;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.02);
  text-align: left; /* 글자 왼쪽 정렬 명시 */
}

.category-tag { color: #81532e; font-size: 0.9rem; font-weight: 700; margin-bottom: 8px; display: block; }
.book-title { font-size: 2.2rem; margin: 8px 0; font-weight: 700; color: #4a3423; line-height: 1.3; }
.book-author { font-size: 1.2rem; color: #6d5d50; margin-bottom: 24px; padding-bottom: 15px; border-bottom: 1px solid #f5ece0; }

/* 정보 그리드 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 25px;
  padding: 20px;
  background: #fdfaf5;
  border-radius: 4px;
}

.info-item { color: #5a4a3a; font-size: 0.95rem; }
.info-item strong { color: #81532e; margin-right: 12px; display: inline-block; width: 140px; }
.highlight { color: #81532e; font-weight: 700; }

.book-description {
  color: #3e342d;
  line-height: 1.8;
  font-size: 1rem;
  white-space: pre-line;
}

/* 도서관 현황 섹션 헤더 (중앙 정렬) */
.section-header-classic {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}
.decoration-line { height: 1px; width: 40px; background-color: #d1b894; }
.section-title { font-size: 1.2rem; color: #4a3423; font-weight: 700; }

/* 도서관 리스트 복구: 양끝 정렬 */
.library-list { display: flex; flex-direction: column; gap: 12px; }
.lib-item { 
  padding: 18px; 
  border: 1px solid #f5ece0; 
  background: #fffcf9;
  border-radius: 4px;
}
.lib-header { 
  display: flex; 
  justify-content: space-between; /* 이름과 거리 양옆으로 */
  align-items: center;
  margin-bottom: 12px; 
}
.lib-name { font-weight: 700; color: #4a3423; }
.lib-distance { color: #81532e; font-size: 0.85rem; font-weight: 600; }

.lib-footer { 
  display: flex; 
  justify-content: space-between; /* 배지와 링크 양옆으로 */
  align-items: center; 
}
.status-badge { font-size: 0.85rem; font-weight: 700; padding: 4px 8px; border-radius: 2px; }
.status-badge.available { color: #2d6a4f; background: #d8f3dc; }
.status-badge.unavailable { color: #a4161a; background: #ffcccb; }
.lib-link { font-size: 0.85rem; color: #81532e; text-decoration: underline; font-weight: 600; }

.library-disclaimer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #d1b894;
  font-size: 0.85rem;
  color: #967979;
  line-height: 1.5;
}
</style>