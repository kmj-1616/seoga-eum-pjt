<template>
  <div v-if="book" class="detail-container">
    <aside class="side-panel">
      <div class="cover-card">
        <img :src="book.cover_url" alt="Book Cover" class="book-cover" />
      </div>
      
      <div class="action-buttons">
        <router-link :to="`/community/${book.isbn}`" class="btn-chat">
          <i class="icon">💬</i> 함께 읽어요
        </router-link>
        
        <button @click="toggleAction('owned')" :class="['btn-owned', { active: book.is_owned }]">
          <i class="icon">{{ book.is_owned ? '✅' : '📚' }}</i> 소장 중이에요
        </button>

        <button @click="toggleAction('wish')" :class="['btn-wish', { active: book.is_wish }]">
          <i class="icon">{{ book.is_wish ? '❤️' : '🤍' }}</i> 구매 원해요
        </button>
      </div>
    </aside>

    <main class="main-content">
      <section class="info-card">
        <span class="category-tag">{{ book.category_name }}</span>
        <h1 class="book-title">{{ book.title }}</h1>
        <h2 class="book-author">{{ book.author }}</h2> <div class="info-grid">
          <div class="info-item"><strong>출판사</strong> {{ book.publisher }}</div>
          <div class="info-item"><strong>출판년도</strong> {{ book.pub_year }}</div>
          <div class="info-item"><strong>ISBN</strong> {{ book.isbn }}</div>
          <div class="info-item"><strong>총 대출 횟수</strong> <span class="highlight">{{ book.loan_count }}회</span></div>
        </div>
        
        <div class="book-description">
          <p>{{ book.description }}</p>
        </div>
      </section>

      <section class="library-card">
        <h2 class="section-title">
          <i class="icon-loc">📍</i> 내 주변 및 관심 도서관 현황
        </h2>
        
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
          대출 가능 여부는 조회일 기준 전날 기준으로 제공됩니다. 실시간 현황은 도서관 홈페이지에서 확인해 주세요.
          </p>
        </div>
      </section>
    </main>
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
    if (confirm("로그인이 필요한 서비스입니다.\n로그인 페이지로 이동하시겠습니까?")) {
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
.detail-container {
  display: flex;
  gap: 40px;
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 20px;
}

.side-panel { flex: 0 0 300px; }

.cover-card {
  background: #fff;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  margin-bottom: 25px;
}

.book-cover { width: 100%; display: block; }

/* 액션 버튼 스타일 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-chat, button {
  padding: 15px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-chat { background: #3b82f6; color: white; }
.btn-chat:hover { background: #2563eb; }

.btn-owned { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-owned.active { border-color: #10b981; color: #10b981; background: #ecfdf5; }

.btn-wish { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-wish.active { border-color: #ef4444; color: #ef4444; background: #fef2f2; }

/* 메인 콘텐츠 스타일 */
.main-content { flex: 1; display: flex; flex-direction: column; gap: 25px; }

.info-card, .library-card {
  background: white;
  padding: 35px;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.category-tag { color: #94a3b8; font-size: 0.9rem; font-weight: 600; }
.book-title { font-size: 2rem; margin: 8px 0 4px; font-weight: 800; color: #1e293b; }
.book-author { font-size: 1.2rem; color: #64748b; margin-bottom: 24px; font-weight: 500; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 25px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.info-item { color: #475569; font-size: 0.95rem; }
.info-item strong { color: #1e293b; margin-right: 8px; width: 80px; display: inline-block; }
.highlight { color: #3b82f6; font-weight: 700; }

.book-description {
  color: #334155;
  line-height: 1.8;
  white-space: pre-line;
}

/* 도서관 현황 스타일 */
.section-title { font-size: 1.2rem; margin-bottom: 20px; font-weight: 700; color: #1e293b; }
.library-list { display: flex; flex-direction: column; gap: 12px; }
.lib-item { padding: 18px; border: 1px solid #e2e8f0; border-radius: 12px; transition: 0.2s; }
.lib-item:hover { border-color: #3b82f6; }
.lib-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
.lib-name { font-weight: 700; color: #1e293b; }
.lib-distance { color: #94a3b8; font-size: 0.85rem; }
.lib-footer { display: flex; justify-content: space-between; align-items: center; }
.status-badge { font-size: 0.85rem; font-weight: 700; padding: 4px 8px; border-radius: 6px; }
.status-badge.available { color: #059669; background: #ecfdf5; }
.status-badge.unavailable { color: #dc2626; background: #fef2f2; }
.lib-link { font-size: 0.85rem; color: #3b82f6; text-decoration: none; font-weight: 600; }

.library-disclaimer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #e2e8f0;
  font-size: 0.85rem;
  color: #94a3b8; /* 차분한 회색 처리 */
  line-height: 1.5;
  word-break: keep-all; /* 한글 단어 끊김 방지 */
}
</style>