<template>
  <div class="profile-container">
    <section class="user-info-card">
      <div class="user-profile-img"></div>
      <div class="user-details">
        <h3>{{ nickname }}님의 서재</h3>
        <p class="user-email">서가이음과 함께 지혜를 나누는 중입니다.</p>
      </div>
    </section>

    <div class="my-library-tabs">
      <button class="tab-btn active">관심 서책</button>
      <button class="tab-btn">읽은 기록</button>
    </div>

    <div class="library-content">
      <div v-if="myBooks.length > 0" class="book-grid">
        </div>
      <div v-else class="empty-library">
        <p>서재가 비어있습니다. 새로운 지혜를 담아보세요.</p>
        <router-link to="/search" class="go-search">서적 탐색하러 가기</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const nickname = ref(localStorage.getItem('user_nickname') || '사용자')
const myBooks = ref([])

const getMyLibrary = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const res = await axios.get('http://127.0.0.1:8000/api/v1/users/library/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    myBooks.value = res.data
  } catch (err) {
    console.error("서재 데이터 로드 실패", err)
  }
}

onMounted(getMyLibrary)
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
}

.user-info-card {
  display: flex;
  align-items: center;
  gap: 30px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  border: 1px solid #d1b894;
  margin-bottom: 40px;
}

.user-profile-img {
  width: 100px;
  height: 100px;
  background-color: #f0f0f0;
  border-radius: 50%;
}

.my-library-tabs {
  display: flex;
  gap: 20px;
  border-bottom: 2px solid #eee;
  margin-bottom: 30px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
}

.tab-btn.active {
  border-bottom: 2px solid #81532e;
  color: #81532e;
  font-weight: bold;
}
</style>