<template>
  <div class="search-container">
    <header class="search-header">
      <h2 class="main-title">서적 탐색</h2>
      <p class="sub-title">원하시는 서적을 검색하고 서가이음의 지혜를 만나보세요.</p>
    </header>

    <div class="search-filter-card">
      <div class="search-input-group">
        <div class="input-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="도서명, 저자, ISBN으로 검색"
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
          총 <span>{{ results.length }}</span>권의 도서
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
      <div v-if="loading" class="state-message">서책을 찾는 중입니다...</div>

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
        <p class="empty-msg">검색 결과가 없습니다.</p>
        <p class="empty-sub">다른 검색어나 카테고리를 선택해 보세요.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// 상태 관리
const searchQuery = ref('')
const categories = ref([]) // ★ 기존 ['전체', '소설'...] 배열 삭제하고 빈 배열로 시작
const selectedCategoryId = ref(null) // ★ 텍스트 대신 DB의 ID(PK)값으로 비교
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

// 2. 검색 로직 (백엔드 BookListView 연동)
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      q: searchQuery.value,
      // ★ 텍스트가 아니라 DB의 ID값을 category 파라미터로 보냄
      category: selectedCategoryId.value || '', 
      sort: sortBy.value
    }
    
    const response = await axios.get('http://127.0.0.1:8000/api/v1/book/', { params })
    
    // 백엔드 페이지네이션이 있다면 results 필드 접근, 없다면 data 전체 사용
    const finalData = response.data.results || response.data
    results.value = finalData
  } catch (error) {
    console.error("검색 중 오류 발생:", error)
  } finally {
    loading.value = false
  }
}

// 3. 카테고리 선택 처리
const selectCategory = (catId) => {
  selectedCategoryId.value = catId // ID값 저장
  handleSearch()
}

const goToDetail = (isbn) => {
  router.push(`/books/${isbn}`)
}

onMounted(async () => {
  await fetchCategories() // 페이지 열리자마자 카테고리 목록부터 긁어옴
  handleSearch()         // 그 다음 첫 화면 검색 결과 로드
})

</script>

<style scoped>
/* 구글 폰트 적용 전제 */
.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
  font-family: 'Nanum Myeongjo', serif;
}

.search-header {
  margin-bottom: 40px;
  text-align: left;
}

.main-title { font-size: 32px; font-weight: 800; color: #1a1a1a; margin-bottom: 8px; }
.sub-title { font-size: 16px; color: #666; }

/* 검색 박스 */
.search-filter-card {
  background: #fff;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  margin-bottom: 50px;
}

.search-input-group {
  display: flex;
  gap: 12px;
  margin-bottom: 25px;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f4f4f4;
  padding: 0 20px;
  border-radius: 12px;
}

.search-icon { font-size: 18px; margin-right: 10px; }

.input-wrapper input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 16px 0;
  font-size: 16px;
  outline: none;
}

.search-btn {
  background: #111;
  color: #fff;
  border: none;
  
  /* 1. padding 대신 명확한 가로/세로 크기 지정 */
  width: 100px;   /* 원하는 가로 크기 */
  height: 50px;   /* input 박스와 높이를 맞추면 깔끔합니다 */
  
  /* 2. 글자 크기 조절 */
  font-size: 20px; /* 원하는 크기로 조절해도 버튼 크기는 불변 */
  
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
  
  /* 3. 글자를 버튼 중앙에 배치 (필수) */
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover { background: #333; }

/* 카테고리 태그 */
.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 30px;
}

.tag {
  background: #fff;
  border: 1px solid #ddd;
  padding: 8px 18px;
  border-radius: 25px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}

.tag.active {
  background: #111;
  color: #fff;
  border-color: #111;
}

/* 메타 정보 */
.search-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.total-count { font-size: 15px; color: #444; }
.total-count span { color: #81532e; font-weight: 800; }

.sort-options select {
  border: none;
  background: transparent;
  font-size: 15px;
  color: #222;
  cursor: pointer;
  outline: none;
}

/* 결과 그리드 */
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 40px 30px;
}

.book-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.book-card:hover { transform: translateY(-8px); }

.book-cover-wrapper {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin-bottom: 15px;
}

.book-cover { width: 100%; height: 100%; object-fit: cover; }

.book-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 6px;
  line-height: 1.4;
  /* 말줄임표 */
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author { font-size: 14px; color: #888; margin-bottom: 10px; }

.category-label {
  font-size: 11px;
  color: #81532e;
  border: 1px solid #81532e;
  padding: 2px 6px;
  border-radius: 4px;
}

.state-message, .empty-state {
  text-align: center;
  padding: 100px 0;
  color: #999;
}
</style>