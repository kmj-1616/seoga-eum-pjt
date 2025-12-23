<template>
  <div class="search-page-container">
    <section class="search-header">
      <h2 class="search-title">도서 탐색</h2>
      <div class="search-input-wrapper">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="handleSearch"
          placeholder="서적명, 저자, 혹은 키워드를 입력하세요..."
        >
        <button @click="handleSearch" class="search-btn">검색</button>
      </div>
    </section>

    <div class="search-results-section">
      <p v-if="results.length > 0" class="result-count">총 {{ results.length }}권의 서책을 찾았습니다.</p>
      
      <div v-if="results.length > 0" class="book-grid">
        <div v-for="book in results" :key="book.id" class="book-card">
          <div class="book-cover-wrapper">
            <img :src="book.cover_url" alt="커버" class="book-cover">
          </div>
          <div class="book-info">
            <h4 class="book-title">{{ book.title }}</h4>
            <p class="book-author">{{ book.author }}</p>
            <button class="btn-detail">상세보기</button>
          </div>
        </div>
      </div>

      <div v-else-if="!isSearching" class="empty-state">
        <p>찾으시는 서책의 이름을 입력해 주십시오.</p>
      </div>
      <div v-else class="loading-state">서책을 찾는 중입니다...</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const results = ref([])
const isSearching = ref(false)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  isSearching.value = true
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/books/search/`, {
      params: { q: searchQuery.value }
    })
    results.value = response.data
  } catch (err) {
    console.error("검색 실패:", err)
  } finally {
    isSearching.value = false
  }
}
</script>

<style scoped>
.search-page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Nanum Myeongjo', serif;
}

.search-header {
  text-align: center;
  margin-bottom: 50px;
}

.search-title {
  font-size: 32px;
  color: #4a3423;
  margin-bottom: 20px;
}

.search-input-wrapper {
  display: flex;
  justify-content: center;
  gap: 10px;
  max-width: 600px;
  margin: 0 auto;
}

.search-input-wrapper input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #d1b894;
  border-radius: 4px;
  outline: none;
}

.search-btn {
  padding: 0 30px;
  background-color: #81532e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 30px;
}
/* 기존 HomeView의 book-card 스타일과 유사하게 유지 */
</style>