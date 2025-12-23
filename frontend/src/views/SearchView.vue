<template>
  <div class="search-outer-container">
    <div class="search-container">
      <header class="search-header">
        <h2 class="main-title">서적 탐색</h2>
        <p class="sub-title">서가에 꽂힌 수많은 지혜 중 당신에게 닿을 한 권을 찾아보세요.</p>
      </header>

      <div class="search-filter-card">
        <div class="search-input-group">
          <div class="input-wrapper">
            <span class="search-icon">🔍</span>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="도서명, 저자, ISBN으로 검색하십시오..."
              @keyup.enter="handleSearch"
            >
          </div>
          <button class="search-btn" @click="handleSearch">탐색</button>
        </div>

        <div class="category-tags">
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            :class="['tag', { active: selectedCategoryId === cat.id }]"
            @click="selectCategory(cat.id)"
          >
            {{ cat.name }}
          </button>
        </div>

        <div class="search-meta">
          <div class="total-count">
            현재 <span>{{ results.length }}</span>권의 서책이 탐색되었습니다.
          </div>
          <div class="sort-options">
            <select v-model="sortBy" @change="handleSearch">
              <option value="popular">인기순</option>
              <option value="latest">최신순</option>
              <option value="title">제목순</option>
            </select>
          </div>
        </div>
      </div>

      <section class="results-section">
        <div v-if="loading" class="state-message">서고에서 책을 꺼내오는 중입니다...</div>

        <div v-else-if="results.length > 0" class="book-grid">
          <div v-for="book in results" :key="book.id" class="book-card" @click="goToDetail(book.isbn)">
            <div class="book-cover-wrapper">
              <img :src="book.cover_url || 'https://via.placeholder.com/150x220'" alt="표지" class="book-cover">
            </div>
            <div class="book-info">
              <h4 class="book-title">{{ book.title }}</h4>
              <p class="book-author">{{ book.author }}</p>
              <div class="book-tags">
                <span class="category-label">{{ book.category_name || '도서' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p class="empty-msg">탐색된 서책이 없습니다.</p>
          <p class="empty-sub">다른 검색어나 카테고리를 선택해 보시기 바랍니다.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 상태 관리
const searchQuery = ref('')
const categories = ref([]) 
const selectedCategoryId = ref(null) 
const sortBy = ref('popular')
const results = ref([])
const loading = ref(false)

// 1. DB에서 카테고리 목록(books_category) 가져오기
const fetchCategories = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/categories/')
    // DRF 응답 구조에 따라 데이터를 categories에 저장
    const data = response.data.results || response.data
    categories.value = [{ id: null, name: '전체' }, ...data]
  } catch (error) {
    console.error("카테고리 로드 실패:", error)
  }
}

// 2. 검색 로직 (백엔드 BookListView 연동, 파라미터 확인)
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      q: searchQuery.value,
      category: selectedCategoryId.value || '', 
      sort: sortBy.value
    }
    
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/', { params })
    
    // 백엔드 페이지네이션이 있다면 results 필드 접근, 없다면 data 전체 사용
    const finalData = response.data.results || response.data
    results.value = finalData
  } catch (error) {
    console.error("검색 중 오류 발생:", error)
  } finally {
    loading.value = false
  }
}

// URL 쿼리 파라미터를 searchQuery 변수에 동기화하는 함수
const syncQueryWithUrl = () => {
  if (route.query.q) {
    searchQuery.value = route.query.q
  } else {
    searchQuery.value = ''
  }
}

onMounted(async () => {
  await fetchCategories()
  syncQueryWithUrl() // 1. 진입 시 URL에 'q'가 있는지 확인
  handleSearch()     // 2. 그 값으로 검색 실행
})

// 검색 페이지에 이미 머무는 상태에서 검색창(Header 등)을 통해 검색어가 바뀔 때 대응
watch(() => route.query.q, () => {
  syncQueryWithUrl()
  handleSearch()
})

// 카테고리 선택 처리
const selectCategory = (catId) => {
  selectedCategoryId.value = catId // ID값 저장
  handleSearch()
}

const goToDetail = (isbn) => {
  router.push(`/book/${isbn}`)
}

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500;600;700&display=swap');

.search-outer-container {
  background-color: #fdfaf5;
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png');
  min-height: 100vh;
  font-family: 'Hahmlet', serif;
}

.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px;
}

.search-header {
  margin-bottom: 40px;
  text-align: center;
}

.main-title { 
  font-size: 36px; 
  font-weight: 800; 
  color: #4a3423; 
  margin-bottom: 12px;
  letter-spacing: 2px;
}
.sub-title { font-size: 18px; color: #81532e; font-weight: 300; }

/* 검색 박스 */
.search-filter-card {
  background: #fff;
  padding: 40px;
  border: 1px solid #d1b894;
  box-shadow: 10px 10px 20px rgba(0,0,0,0.02);
  margin-bottom: 50px;
}

.search-input-group {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: #fdfcfb;
  padding: 0 20px;
  border: 1px solid #e5e7eb;
}

.input-wrapper:focus-within {
  border-color: #81532e;
}

.search-icon { font-size: 18px; margin-right: 12px; color: #81532e; }

.input-wrapper input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 16px 0;
  font-size: 16px;
  font-family: 'Hahmlet', serif;
  outline: none;
  color: #4a3423;
}

.input-wrapper input::placeholder {
  color: #c4b5a6;
}

.search-btn {
  background: #81532e;
  color: #fdfaf5;
  border: 1px solid #4a3423;
  width: 120px;
  height: 54px;
  font-size: 18px;
  font-family: 'Hahmlet', serif;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover { background: #4a3423; }

/* 카테고리 태그 */
.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 35px;
  justify-content: center;
}

.tag {
  background: #fdfaf5;
  border: 1px solid #f5ece0;
  padding: 8px 22px;
  border-radius: 4px; 
  font-size: 14px;
  font-family: 'Hahmlet', serif;
  color: #6d5d50;
  cursor: pointer;
  transition: 0.2s;
}

.tag:hover {
  border-color: #81532e;
  color: #81532e;
}

.tag.active {
  background: #81532e;
  color: #fff;
  border-color: #4a3423;
}

/* 메타 정보 */
.search-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 25px;
  border-top: 1px solid #f5ece0;
}

.total-count { font-size: 15px; color: #6d5d50; }
.total-count span { color: #81532e; font-weight: 700; }

.sort-options select {
  border: 1px solid transparent;
  background: transparent;
  font-family: 'Hahmlet', serif;
  font-size: 15px;
  color: #4a3423;
  cursor: pointer;
  outline: none;
  padding: 5px;
}

.sort-options select:hover {
  color: #81532e;
}

/* 결과 그리드 */
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 50px 30px;
}

.book-card {
  cursor: pointer;
  transition: transform 0.3s ease;
  background: white;
  padding: 15px;
  border: 1px solid transparent;
}

.book-card:hover { 
  transform: translateY(-10px);
  border-color: #f5ece0;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
}

.book-cover-wrapper {
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
  margin-bottom: 18px;
}

.book-cover { width: 100%; height: 100%; object-fit: cover; }

.book-info { text-align: left; }

.book-title {
  font-size: 16px;
  font-weight: 700;
  color: #4a3423;
  margin-bottom: 8px;
  line-height: 1.4;
  height: 2.8em; /* 두 줄 높이 고정 */
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.book-author { font-size: 14px; color: #888; margin-bottom: 12px; }

.category-label {
  font-size: 11px;
  color: #81532e;
  background: #fdfaf5;
  border: 1px solid #81532e;
  padding: 2px 8px;
  border-radius: 2px;
}

.state-message, .empty-state {
  text-align: center;
  padding: 120px 0;
  color: #81532e;
  font-size: 18px;
}

.empty-sub {
  font-size: 15px;
  color: #c4b5a6;
  margin-top: 10px;
}
</style>