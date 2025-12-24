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
            <p class="loan-info">최근 3개월간 대출 {{ book.loan_count.toLocaleString() }}회</p>
          </div>
        </div>
      </div>
    </section>

    <section class="recommend-section community-section">
      <div class="section-header">
        <span class="decoration-line"></span>
        <h3 class="section-title">활발한 독서 커뮤니티</h3>
        <span class="decoration-line"></span>
      </div>

      <div class="community-grid">
        <div v-for="room in activeRooms" :key="room.isbn" class="community-card" @click="goToCommunity(room.isbn)">
          <div class="room-top">
            <span class="room-icon">📘</span>
            <h4 class="room-title">{{ room.title }}</h4>
          </div>
          <div class="room-stats">
            <span class="stat-item">👥 {{ room.user_count }}명 참여</span>
            <span class="stat-item">💬 {{ room.message_count }}개 메시지</span>
          </div>
        </div>
      </div>

      <!-- <div class="service-banner-grid">
        <div class="service-card">
          <div class="service-icon ai">📘</div>
          <h4>AI 맞춤 추천</h4>
          <p>독서 기록과 선호 데이터를 AI가 분석하여 당신에게 딱 맞는 도서를 추천합니다</p>
        </div>
        <div class="service-card">
          <div class="service-icon community">👥</div>
          <h4>독서 커뮤니티</h4>
          <p>같은 책을 읽는 독자들과 실시간으로 소통하고 생각을 나눠보세요</p>
        </div>
        <div class="service-card">
          <div class="service-icon trade">🛍️</div>
          <h4>중고책 거래</h4>
          <p>공공도서관 보관함을 활용한 안전하고 편리한 중고책 거래를 경험하세요</p>
        </div>
      </div> -->
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
const activeRooms = ref([])

const startAutoScroll = () => {
  return setInterval(() => {
    if (topGrid.value) {
      const el = topGrid.value
      const maxScroll = el.scrollWidth - el.clientWidth
      
      if (el.scrollLeft >= maxScroll - 10) {
        el.scrollTo({ left: 0, behavior: 'smooth' })
      } else {
        el.scrollBy({ left: 250, behavior: 'smooth' })
      }
    }
  }, 3000)
}

let topInterval 

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
    // 1. 인기 서책 로드
    const topRes = await axios.get('http://127.0.0.1:8000/api/v1/books/', { params: { sort: 'popular' } })
    const bookList = topRes.data.results || topRes.data; 
    topBooks.value = bookList.slice(0, 10);

    // 2. 추천 서책 로드 (로그인 시)
    if (status) {
      try {
        const recRes = await axios.get('http://127.0.0.1:8000/api/v1/books/recommendations/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        recommendations.value = recRes.data
      } catch (e) { console.error("추천 데이터 로드 실패", e) }
    }

    // 3. 활발한 커뮤니티 데이터 로드 (이 부분을 아래처럼 교체하세요)
    try {
      const commRes = await axios.get('http://127.0.0.1:8000/api/v1/community/active-rooms/')
      activeRooms.value = commRes.data.slice(0, 3)
    } catch (commErr) {
      console.warn("커뮤니티 API가 아직 준비되지 않아 더미 데이터를 표시합니다.")
      // API 연결 전까지 화면을 확인하기 위한 더미 데이터입니다.
      activeRooms.value = [
        { isbn: '9788936434120', title: '데미안', user_count: 24, message_count: 156 },
        { isbn: '9788937460753', title: '1984', user_count: 18, message_count: 89 },
        { isbn: '9788936433598', title: '채식주의자', user_count: 31, message_count: 203 }
      ]
    }

  } catch (err) {
    console.error("전체 데이터 로드 중 치명적 오류:", err)
  }
}

onMounted(async () => {
  await fetchData()
  topInterval = startAutoScroll() 
  
  window.addEventListener('auth-change', fetchData)
})

onUnmounted(() => {
  if (topInterval) clearInterval(topInterval)
  window.removeEventListener('auth-change', fetchData)
})

const goToDetail = (isbn) => {
  if (!isbn) return;
  router.push({ name: 'bookdetail', params: { isbn: String(isbn) } });
}

const goToCommunity = (isbn) => {
  if (!isbn) return;
  router.push(`/community/${isbn}`);
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

.search-button {
  background-color: #f5ece0; 
  border: none;
  width: 70px;
  height: 100%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  color: #81532e; 
  font-size: 24px;
  transition: all 0.2s ease;
}

.search-button:hover {
  background-color: #e8ddcc; 
  color: #4a3423; 
}

.recommend-section { max-width: 1200px; margin: 60px auto; text-align: center; }
.section-header { display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px; }
.decoration-line { height: 1px; width: 50px; background-color: #81532e; }
.section-title { font-size: 34px; color: #4a3423; font-weight: 700; }
.section-desc { color: #967979; font-size: 24px; margin-bottom: 30px; }

.book-grid-fixed {
  display: flex;
  flex-wrap: nowrap;
  justify-content: space-between;
  gap: 15px;
  padding: 20px 0;
  width: 100%;
}

.book-grid-scroll {
  display: flex;
  gap: 30px;
  overflow-x: auto;
  white-space: nowrap;
  scroll-behavior: smooth;
  scrollbar-width: none;
  padding: 20px 10px;
}
.book-grid-scroll::-webkit-scrollbar { display: none; }

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
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 16px; font-weight: 700; color: #4a3423;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.book-author { font-size: 14px; color: #888; margin-bottom: 8px; }

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

.community-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  margin: 30px 0 60px 0;
}

.community-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border: 1px solid #eee;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
}

.community-card:hover {
  transform: translateY(-7px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border-color: #d1b894;
}

.room-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
}

.room-icon {
  font-size: 20px;
  color: #4a90e2; /* 이미지의 푸른 아이콘 느낌 */
}

.room-title {
  font-size: 20px;
  font-weight: 700;
  color: #4a3423;
  margin: 0;
}

.room-stats {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #f5f5f5;
  padding-top: 15px;
}

.stat-item {
  font-size: 14px;
  color: #666;
}

/* 하단 서비스 안내 배너 스타일 */
.service-banner-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 40px;
}

.service-card {
  background: #ffffff;
  padding: 30px;
  border-radius: 15px;
  text-align: left;
  border: 1px solid #f0f0f0;
}

.service-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 20px;
}

/* 서비스별 아이콘 배경색 */
.service-icon.ai { background-color: #eef2ff; color: #4f46e5; }
.service-icon.community { background-color: #f0fdf4; color: #16a34a; }
.service-icon.trade { background-color: #faf5ff; color: #9333ea; }

.service-card h4 {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.service-card p {
  font-size: 14px;
  color: #777;
  line-height: 1.6;
  margin: 0;
}
</style>