<template>
  <div class="profile-container" v-if="userInfo">
    <header class="profile-header">
      <h1 class="main-title">마이페이지</h1>
      <p class="sub-title">나의 독서 활동과 정보를 관리하세요</p>
    </header>

    <div class="user-card">
      <div class="avatar-circle">
        {{ userInfo.nickname ? userInfo.nickname[0] : userInfo.username[0] }}
      </div>
      <div class="user-content">
        <div class="user-top-line">
          <h2 class="user-name">{{ userInfo.nickname || userInfo.username }}</h2>
          <button class="edit-info-btn">📝 정보 수정</button>
        </div>
        <p class="user-email">{{ userInfo.email }}</p>
        
        <div class="preference-tags">
          <span class="p-tag gray">20대</span>
          <span class="p-tag gray">여성</span>
          <span v-for="tag in userInfo.preferred_categories" :key="tag" class="p-tag">
            {{ tag }}
          </span>
        </div>
        <p class="user-location">📍 {{ userInfo.address || '주소 정보가 없습니다.' }}</p>
      </div>
    </div>

    <nav class="info-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-item', { active: currentTab === tab.id }]"
        @click="currentTab = tab.id"
      >
        {{ tab.icon }} {{ tab.name }}
      </button>
    </nav>

    <section class="shelf-section" v-if="currentTab === 'shelf'">
      <h3 class="section-title">소장 중인 도서</h3>
      <div v-if="ownedBooks.length > 0" class="shelf-grid">
        <div v-for="book in ownedBooks" :key="book.id" class="shelf-card">
          <div class="shelf-info">
            <h4 class="shelf-book-title">{{ book.title }}</h4>
            <p class="shelf-book-author">{{ book.author }}</p>
            <div class="shelf-badges">
              <span class="badge owned">소장중</span>
              <span v-if="book.price" class="badge price">{{ book.price.toLocaleString() }}원</span>
            </div>
          </div>
          <button class="sell-btn" :class="{ selling: book.is_selling }">
            {{ book.is_selling ? '판매중' : '판매 등록' }}
          </button>
        </div>
      </div>
      <div v-else class="empty-shelf">
        소장 중인 도서가 없습니다. 서책을 등록해 보세요.
      </div>
    </section>

    <section v-else class="empty-state">
      해당 서비스는 준비 중입니다.
    </section>
  </div>

  <div v-else class="loading-state">
    <p>사용자 정보를 불러오는 중입니다...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const userInfo = ref(null)
const ownedBooks = ref([])

// ★ 아래 변수들이 누락되어 에러가 났던 겁니다. 꼭 추가하세요!
const currentTab = ref('shelf') // 현재 선택된 탭 (기본값: 나의 서가)
const tabs = [
  { id: 'shelf', name: '나의 서가', icon: '📱' },
  { id: 'activity', name: '나의 활동', icon: '💭' },
  { id: 'history', name: '거래 내역', icon: '👜' }
]

// 3. 유저 정보 가져오기 (주소 및 인증 로직 수정)
const fetchUserProfile = async () => {
  const token = localStorage.getItem('token') || 
                localStorage.getItem('access') || 
                localStorage.getItem('access_token');
  
  if (!token) return;

  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/users/profile/', {
      headers: { 
        // JWT 방식이므로 'Token' 대신 'Bearer'를 사용해야 합니다.
        Authorization: `Bearer ${token}` 
      }
    });
    userInfo.value = response.data;
  } catch (error) {
    console.error("에러 발생:", error.response);
  }
}

// 4. 내 소장 도서 가져오기
const fetchMyOwnedBooks = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/', {
      params: { owned: 'true' },
      headers: { Authorization: `Bearer ${token}` }
    })
    ownedBooks.value = response.data.results || response.data
  } catch (error) {
    console.error("소장 도서 로드 실패:", error)
  }
}

onMounted(async () => {
  await fetchUserProfile()
  await fetchMyOwnedBooks()
})
</script>

<style scoped>
.profile-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Nanum Gothic', sans-serif;
}

.main-title { font-size: 32px; font-weight: 800; margin-bottom: 8px; letter-spacing: -1px; }
.sub-title { color: #666; margin-bottom: 40px; font-size: 16px; }

/* 유저 카드 스타일 */
.user-card {
  display: flex;
  gap: 35px;
  padding: 40px;
  background: #fdfdfd;
  border: 1px solid #eaeaea;
  border-radius: 20px;
  margin-bottom: 45px;
  align-items: center;
}

.avatar-circle {
  width: 110px;
  height: 110px;
  background: #f0f2f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: #888;
  font-weight: bold;
}

.user-content { flex: 1; }
.user-top-line { display: flex; justify-content: space-between; align-items: center; }
.user-name { font-size: 26px; font-weight: 700; margin: 0; }

.edit-info-btn {
  padding: 10px 18px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: 0.2s;
}

.user-email { color: #5c6b80; margin: 10px 0 18px; font-size: 15px; }

.preference-tags { display: flex; gap: 8px; margin-bottom: 18px; flex-wrap: wrap; }
.p-tag {
  padding: 5px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #4a5568;
  background: #fff;
}
.p-tag.gray { background: #f7fafc; color: #718096; border: none; }

.user-location { font-size: 14px; color: #718096; margin: 0; }

/* 탭 스타일 */
.info-tabs {
  display: flex;
  background: #f1f3f5;
  padding: 6px;
  border-radius: 14px;
  margin-bottom: 40px;
}

.tab-item {
  flex: 1;
  padding: 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 10px;
  font-weight: 600;
  color: #495057;
  transition: 0.3s;
}

.tab-item.active {
  background: #fff;
  color: #111;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* 도서 목록 스타일 */
.section-title { font-size: 22px; font-weight: 700; margin-bottom: 25px; }

.shelf-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: #fff;
  border: 1px solid #f1f3f5;
  border-radius: 16px;
  margin-bottom: 18px;
  transition: 0.2s;
}

.shelf-card:hover { border-color: #dee2e6; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }

.shelf-book-title { font-size: 19px; font-weight: 700; margin: 0 0 6px 0; color: #1a1a1a; }
.shelf-book-author { font-size: 15px; color: #868e96; margin-bottom: 12px; }

.shelf-badges { display: flex; gap: 8px; }
.badge { font-size: 12px; padding: 4px 10px; border-radius: 6px; font-weight: 700; }
.badge.owned { background: #edf2ff; color: #3b5bdb; }
.badge.price { background: #37b24d; color: #fff; }

.sell-btn {
  padding: 12px 24px;
  border: 1px solid #dee2e6;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  font-weight: 700;
  font-size: 14px;
  transition: 0.2s;
}

.sell-btn:hover:not(.selling) { background: #f8f9fa; border-color: #adb5bd; }
.sell-btn.selling { color: #adb5bd; border: none; background: #f1f3f5; cursor: default; }

.empty-shelf, .loading-state {
  text-align: center;
  padding: 80px 0;
  color: #adb5bd;
}
</style>