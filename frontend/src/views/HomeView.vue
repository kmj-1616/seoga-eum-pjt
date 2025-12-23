<template>
  <div class="home-container">
    <section class="hero-banner">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h2 class="hero-top-text">과거와 현재를 잇는 지혜의 서가</h2>
        <p class="hero-subtitle">당신만을 위한 고유한 책의 숨결을 느껴보세요</p>
        
        <div class="search-bar">
          <input type="text" placeholder="찾으시는 서책의 이름을 입력하십시오..." class="search-input">
          <button class="search-button">
            <img src="@/assets/search-button.jpg" alt="검색" class="search-button-img" />
          </button>
        </div>
      </div>
    </section>

    <section class="recommend-section">
      <div class="section-header">
        <span class="decoration-line"></span>
        <h3 class="section-title">오늘의 추천 서책</h3>
        <span class="decoration-line"></span>
      </div>
      <p class="section-desc">사용자의 취향에 맞춰 선별한 서적들입니다.</p>

      <div v-if="isLoggedIn" class="recommend-content">
        <div v-if="recommendations.length > 0" class="book-grid">
          <div v-for="rec in recommendations" :key="rec.id" class="book-card">
            <div class="book-cover-wrapper">
              <img :src="rec.book.cover_url" alt="서책 표지" class="book-cover">
            </div>
            <div class="book-info">
              <h4 class="book-title">{{ rec.book.title }}</h4>
              <p class="book-author">{{ rec.book.author }}</p>
              <p class="ai-reason">" {{ rec.reason }} "</p>
            </div>
          </div>
        </div>
        <div v-else class="loading-state">추천 서책을 선별 중입니다...</div>
      </div>

      <div v-else class="login-prompt-card">
        <p class="prompt-text">로그인하시면 AI가 분석한 <br> 당신만을 위한 추천 서책을 만나보실 수 있습니다.</p>
        <div class="prompt-btns">
          <router-link to="/login" class="btn-login">로그인</router-link>
          <router-link to="/signup" class="btn-signup">회원가입</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const recommendations = ref([])
const isLoggedIn = ref(false)

const checkStatusAndFetch = () => {
  const token = localStorage.getItem('access_token')
  isLoggedIn.value = !!token
  
  if (isLoggedIn.value) {
    getRecommendations(token)
  } else {
    recommendations.value = [] 
  }
}

const getRecommendations = function (token) {
  axios({
    method: 'get',
    url: 'http://127.0.0.1:8000/api/v1/books/recommendations/',
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(res => { recommendations.value = res.data })
    .catch(err => { 
      if (err.response?.status === 401) {
        isLoggedIn.value = false
        recommendations.value = []
      }
    })
}

const handleAuthChange = () => {
  checkStatusAndFetch()
}

onMounted(() => {
  checkStatusAndFetch()
  
  window.addEventListener('auth-change', handleAuthChange)
  window.addEventListener('storage', handleAuthChange)
})

onUnmounted(() => {
  window.removeEventListener('auth-change', handleAuthChange)
  window.removeEventListener('storage', handleAuthChange)
})

watch(() => route.path, () => {
  checkStatusAndFetch()
})
</script>

<style scoped>
/* 구글에서 폰트 불러오기 */
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');
.home-container {
  font-family: 'Nanum Myeongjo', serif;
  width: 100%;
  padding: 0;
  background-color: #fdfaf5;
  min-height: 100vh;
}

.hero-banner {
  padding-bottom: 60px;
  position: relative;
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

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-top-text {
  font-family: 'Nanum Myeongjo', serif;
  font-size: 50px;
  font-weight: 400;
  letter-spacing: 5px;
  margin-bottom: 20px;
  color: #F5DEB3;
}

.hero-subtitle {
  font-family: 'Nanum Myeongjo', serif;
  font-size: 30px;
  margin-bottom: 40px;
  opacity: 1.2;
  font-weight: 300;
}

.search-bar {
  font-family: 'Nanum Myeongjo', serif;
  display: flex;
  background-color: rgba(255, 255, 255, 0.95);
  border: 2px solid #81532e;
  border-radius: 4px;
  width: 650px;       
  height: 60px;     
  margin: 0 auto;
  overflow: hidden;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
}

.search-input {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: transparent;
  font-size: 16px;
  outline: none;
  color: #4a3423;
}

.search-button {
  background-color: #ffffff;
  border: none;
  padding: 0 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.3s;
}

.search-button:hover {
  background-color: #ffffff;
}

.search-button-img {
  width: 24px;
  height: 24px;
  object-fit: fill;
}

.recommend-section {
  max-width: 1200px;
  margin: 10px auto;
  padding: 0 20px;
  text-align: center;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 4px;
}

.decoration-line {
  height: 1px;
  width: 50px;
  background-color: #81532e;
}

.section-title {
  font-size: 34px;
  color: #4a3423;
  font-weight: 700;
}

.section-desc {
  color: #967979;
  font-size: 26px;
  margin-top: 0;
  margin-bottom: 30px;
}

.search-input::placeholder {
  font-family: 'Nanum Myeongjo', serif;
  letter-spacing: -0.5px;
  font-size: 18px;
  font-weight: 700;
}

.recommend-content {
  margin-top: 40px;
}

.book-grid {
  display: flex;            /* Grid 대신 Flex 사용 */
  gap: 30px;
  max-width: 1100px;        /* 전체 섹션 너비에 맞춰 조절 */
  margin: 0 auto;
  padding: 20px 10px;       /* 그림자가 잘리지 않게 여백 추가 */
  
  /* 가로 스크롤 핵심 설정 */
  overflow-x: auto;         /* 가로 내용이 넘치면 자동 스크롤 생성 */
  white-space: nowrap;      /* 내부 요소들이 줄바꿈되지 않게 설정 */
  -webkit-overflow-scrolling: touch; /* 모바일에서 부드러운 스크롤 */
  
  /* 스크롤바 디자인 (선택 사항: 깔끔하게 숨기거나 얇게 만들기) */
  scrollbar-width: thin; 
  scrollbar-color: #d1b894 transparent;
}

/* 스크롤바 커스텀 (Chrome, Safari) */
.book-grid::-webkit-scrollbar {
  height: 6px;              /* 가로 스크롤바 높이 */
}
.book-grid::-webkit-scrollbar-thumb {
  background-color: #d1b894; /* 스크롤바 색상 */
  border-radius: 10px;
}
.book-grid::-webkit-scrollbar-track {
  background: transparent;
}

.book-card {
  flex: 0 0 220px;          /* ★핵심: 카드가 줄어들지 않고 220px 너비를 유지함 */
  background: white;
  padding: 15px;
  border: 1px solid #eee;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  transition: transform 0.3s;
  display: inline-block;    /* 가로 나열 유지 */
  vertical-align: top;
}

/* 텍스트가 너무 길어지면 말줄임표(...) 처리 (가로 스크롤 시 필수) */
.book-title {
  font-size: 16px;
  color: #4a3423;
  margin: 5px 0;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-card:hover {
  transform: translateY(-10px);
}

.book-cover-wrapper {
  width: 100%;
  aspect-ratio: 2/3;
  background-color: #f0f0f0;
  margin-bottom: 15px;
  overflow: hidden;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-title {
  font-size: 16px;
  color: #4a3423;
  margin: 5px 0;
  font-weight: 700;
}

.book-author {
  font-size: 14px;
  color: #888;
  margin-bottom: 10px;
}

.ai-reason {
  font-family: 'Hahmlet', serif;
  font-size: 12px;
  color: #81532e;
  background: #fdfaf5;
  padding: 8px;
  border-radius: 4px;
  /* 추천 사유가 길어도 한 줄 혹은 일정 높이를 유지하게 설정 */
  white-space: normal;      /* 사유는 여러 줄로 보일 수 있게 함 */
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 비로그인 유도 카드 스타일 */
.login-prompt-card {
  background: #fff;
  border: 1px solid #d1b894;
  padding: 40px;
  margin-top: 30px;
  border-radius: 8px;
}

.prompt-text {
  font-size: 18px;
  color: #4a3423;
  margin-bottom: 25px;
  line-height: 1.6;
}

.prompt-btns {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-login, .btn-signup {
  padding: 10px 25px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 700;
  transition: 0.3s;
}

.btn-login {
  background-color: #81532e;
  color: white;
}

.btn-signup {
  border: 1px solid #81532e;
  color: #81532e;
}

.btn-login:hover { background-color: #5d3b21; }
</style>