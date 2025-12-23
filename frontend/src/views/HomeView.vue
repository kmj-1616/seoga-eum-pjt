<template>
  <div class="home-container">
    <section class="hero-banner">
      <div class="hero-content">
        <h2 class="hero-top-text">서책으로 사람을 잇다, 서가이음</h2>
        <p class="hero-subtitle">함께 나누는 문장부터 손때 묻은 서책의 새로운 인연까지</p>
        <div class="search-bar">
          <input 
            v-model="searchQuery" 
            @keyup.enter="handleSearch" 
            type="text" 
            placeholder="찾으시는 서책의 이름을 입력하십시오..." 
            class="search-input"
          >
          <button @click="handleSearch" class="search-button">🔍</button>
        </div>
      </div>
    </section>

    <section class="recommend-section">
      <div class="section-header">
        <span class="decoration-line"></span>
        <h3 class="section-title">오늘의 추천 서책</h3>
        <span class="decoration-line"></span>
      </div>
      
      <div v-if="isLoggedIn" class="recommend-content">
        <p class="section-desc">
          <span class="nickname-highlight">{{ userNickname }}</span> 님의 취향과 활동을 분석한 추천 서책입니다.
        </p>
        <div v-if="recommendations.length > 0" class="book-grid-fixed">
          <div v-for="rec in recommendations" :key="rec.id" class="book-card" @click="goToDetail(rec.book.isbn)">
            <div class="book-cover-wrapper">
              <img :src="rec.book.cover_url" alt="서책 표지" class="book-cover">
            </div>
            <div class="book-info">
              <h4 class="book-title">{{ rec.book.title }}</h4>
              <p class="book-author">{{ rec.book.author }}</p>
              <div class="ai-reason-container">
                <p class="ai-reason">" {{ rec.reason }} "</p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="loading-state">추천 서책을 선별 중입니다...</div>
      </div>

      <div v-else class="login-prompt-card">
        <p class="prompt-text">서가에 입장하고 AI가 당신만을 위해 추천한 서책을 만나보세요.</p>
        <button @click="router.push('/login')" class="btn-classic">서가 입장하기</button>
      </div>
    </section>

    <section class="recommend-section">
      <div class="section-header">
        <span class="decoration-line"></span>
        <h3 class="section-title">지금 가장 인기 있는 서책</h3>
        <span class="decoration-line"></span>
      </div>
      <div class="book-grid-scroll" ref="topGrid">
        <div v-for="(book, index) in topBooks" :key="book.id" class="book-card" @click="goToDetail(book.isbn)">
          <div class="rank-badge">{{ index + 1 }}</div>
          <div class="book-cover-wrapper">
            <img :src="book.cover_url" alt="서책 표지" class="book-cover">
          </div>
          <div class="book-info">
            <h4 class="book-title">{{ book.title }}</h4>
            <p class="book-author">{{ book.author }}</p>
            <p class="loan-info">누적 대출 {{ book.loan_count.toLocaleString() }}회</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const recommendations = ref([])
const topBooks = ref([])
const isLoggedIn = ref(false)
const searchQuery = ref('')
const topGrid = ref(null)
const userNickname = ref('')

// 1. 자동 슬라이드 로직 정의 
const startAutoScroll = () => {
  return setInterval(() => {
    if (topGrid.value) {
      const el = topGrid.value
      const maxScroll = el.scrollWidth - el.clientWidth
      
      // 스크롤이 끝에 도달하면 처음으로, 아니면 250px씩 이동
      if (el.scrollLeft >= maxScroll - 10) {
        el.scrollTo({ left: 0, behavior: 'smooth' })
      } else {
        el.scrollBy({ left: 250, behavior: 'smooth' })
      }
    }
  }, 3000)
}

let topInterval // 인터벌 ID 보관용 변수

// 2. 데이터를 가져오는 핵심 함수
const fetchData = async () => {
  const token = localStorage.getItem('access_token')
  const status = !!token
  isLoggedIn.value = status 

  if (status) {
    userNickname.value = localStorage.getItem('user_nickname') || '당신'
  } else {
    userNickname.value = ''
    recommendations.value = [] 
  }

  try {
    const topRes = await axios.get('http://127.0.0.1:8000/api/v1/books/', { params: { sort: 'popular' } })
    const bookList = topRes.data.results || topRes.data; 

    topBooks.value = bookList.slice(0, 10);

    if (status) {
      const recRes = await axios.get('http://127.0.0.1:8000/api/v1/books/recommendations/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      recommendations.value = recRes.data
    }
  } catch (err) {
    console.error("데이터 로드 실패:", err)
  }
}

// 3. 생명주기 관리
onMounted(async () => {
  await fetchData()
  topInterval = startAutoScroll() 
  
  // 네브바의 CustomEvent('auth-change')를 수신
  window.addEventListener('auth-change', fetchData)
})

onUnmounted(() => {
  if (topInterval) clearInterval(topInterval)
  window.removeEventListener('auth-change', fetchData)
})

// 4. 이동 및 검색 로직
const goToDetail = (isbn) => {
  if (!isbn) return;
  router.push({ name: 'bookdetail', params: { isbn: String(isbn) } });
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  router.push({ name: 'search', query: { q: searchQuery.value } })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');

.home-container {
  font-family: 'Hahmlet', serif;
  width: 100%;
  background-color: #fdfaf5;
  min-height: 100vh;
}

/* 히어로 배너 유지 */
.hero-banner {
  padding-bottom: 60px;
  background-color: #4a3423; 
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png'); 
  background-blend-mode: overlay;
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  border-bottom: 4px solid #81532e;
}
.hero-top-text { font-size: 50px; letter-spacing: 5px; margin-bottom: 20px; color: #F5DEB3; }
.hero-subtitle { font-size: 30px; margin-bottom: 40px; font-weight: 300; }

/* 검색 바 컨테이너 */
.search-bar {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border: 2px solid #d1b894; 
  width: 650px;
  height: 50px;
  margin: 0 auto;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
  overflow: hidden;
}

/* 입력창 */
.search-input {
  flex: 1;
  padding: 0 20px;
  border: none;
  background: transparent;
  font-size: 16px;
  outline: none;
  font-family: 'Hahmlet', serif;
  color: #4a3423;
}

/* 검색 버튼 - 베이지 스타일 */
.search-button {
  background-color: #f5ece0; 
  border: none;
  width: 70px;
  height: 100%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* 돋보기 아이콘 스타일 */
  color: #81532e; 
  font-size: 24px;
  transition: all 0.2s ease;
}

.search-button:hover {
  background-color: #e8ddcc; 
  color: #4a3423; 
}

/* 레이아웃 디자인 */
.recommend-section { max-width: 1200px; margin: 60px auto; text-align: center; }
.section-header { display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px; }
.decoration-line { height: 1px; width: 50px; background-color: #81532e; }
.section-title { font-size: 34px; color: #4a3423; font-weight: 700; }
.section-desc { color: #967979; font-size: 24px; margin-bottom: 30px; }

/* 1. 고정 그리드 (추천 도서) */
.book-grid-fixed {
  display: flex;
  flex-wrap: nowrap; /* 줄바꿈 절대 금지 */
  justify-content: space-between; /* 5개를 양 끝에 맞춰 균등 배분 */
  gap: 15px; /* 간격을 살짝 좁힘 */
  padding: 20px 0;
  width: 100%; /* 부모 너비를 가득 채움 */
}

/* 2. 자동 슬라이드 그리드 (인기 도서) */
.book-grid-scroll {
  display: flex;
  gap: 30px;
  overflow-x: auto; /* 자동 슬라이드 작동을 위해 필요 */
  white-space: nowrap;
  scroll-behavior: smooth;
  scrollbar-width: none;
  padding: 20px 10px;
}
.book-grid-scroll::-webkit-scrollbar { display: none; }

/* 3. 카드 공통 스타일 */
.book-card {
  flex: 0 0 calc(20% - 15px); 
  min-width: 190px; 
  display: flex;
  flex-direction: column; 
  background: white;
  padding: 15px;
  border: 1px solid #eee;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  transition: transform 0.3s;
  cursor: pointer;
  position: relative;
  height: 400px; 
}
.book-card:hover { transform: translateY(-10px); }

.book-cover-wrapper {
  width: 100%;
  height: 240px; 
  margin-bottom: 12px;
  overflow: hidden;
}
.book-cover { width: 100%; height: 100%; object-fit: cover; }

.book-info {
  flex-grow: 1; /* 남은 공간을 차지하여 하단 정렬 유지 */
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 16px; font-weight: 700; color: #4a3423;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.book-author { font-size: 14px; color: #888; margin-bottom: 8px; }

/* 추천 사유 공간 고정 */
.ai-reason-container {
  height: 50px; 
  display: flex;
  align-items: center;
}
.ai-reason {
  font-family: 'Hahmlet', serif;
  font-size: 12px; color: #81532e; background: #fdfaf5;
  padding: 5px 8px; border-radius: 4px;
  width: 100%;
  white-space: normal;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden;
}

.rank-badge {
  position: absolute; top: -5px; left: -5px;
  background: #81532e; color: #F5DEB3;
  width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;
  font-weight: bold; z-index: 10;
}
.loan-info { font-size: 13px; color: #81532e; font-weight: bold; margin-top: auto; }

.btn-classic { background: #81532e; color: white; padding: 10px 20px; border: none; cursor: pointer; font-family: 'Hahmlet'; font-size: 14px;}
.login-prompt-card { background: #fff; border: 1px solid #d1b894; padding: 40px; border-radius: 8px; }

.nickname-highlight {
  color: #81532e;     
  font-weight: 700;   
  font-size: 1.1em;   
}
</style>