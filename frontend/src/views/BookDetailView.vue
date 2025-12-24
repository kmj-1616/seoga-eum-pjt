<template>
  <div :class="['detail-outer-container', { 'is-loading': !book }]" >
    
    <div class="detail-container" v-if="book">
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
        <transition name="fade-slide">
          <div v-if="book.is_owned" class="selling-input-card">
            
            <div v-if="!isPriceRegistered">
              <p class="input-label">📜 희망 판매 가격을 적어주세요</p>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model="sellingPrice" 
                  placeholder="가격을 입력" 
                  class="price-field"
                />
                <span class="currency">원</span>
                <button @click="registerPrice" class="btn-save">등록</button>
              </div>
            </div>

            <div v-else class="registered-price-view">
              <p class="input-label">✅ 등록된 판매 가격</p>
              <div class="price-display">
                <span class="final-price">{{ sellingPrice.toLocaleString() }}원</span>
                <button @click="editPrice" class="btn-edit-small">수정하기</button>
              </div>
            </div>

          </div>
        </transition>

        <transition name="fade-slide">
          <div v-if="book.is_wish" class="owner-list-card">
            <h4 class="list-title">📍 소장 중인 이웃</h4>
              <div v-if="owners && owners.length > 0" class="owner-items">
                <div v-for="owner in owners" :key="owner.id" class="owner-entry">
                  <div class="owner-info">
                    <div class="main-info">
                      <span class="owner-name">{{ owner.nickname }}</span>
                      <span class="owner-price">{{ owner.price.toLocaleString() }}원</span>
                    </div>
                    <div class="sub-info">
                      <i class="icon-small">🏛️</i> 
                      <span class="owner-lib">{{ owner.libraries }}</span>
                    </div>
                  </div>
                  <button @click="goToChat(owner)" class="btn-tiny-chat">대화하기</button>
                </div>
              </div>
              <p v-else class="no-owner">현재 소장 중인 이웃이 없습니다.</p>
          </div>
        </transition>

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

    <div class="loading-state" v-else>
      <div class="loading-content">
        <div class="spinner"></div>
        <p class="loading-text">서가에서 책을 찾는 중입니다...</p>
      </div>
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

// --- [추가] 새로운 상태 변수 선언 ---
const sellingPrice = ref(null) // 판매자가 입력할 가격
const isPriceRegistered = ref(false) // 가격 등록 여부
const owners = ref([])         // 이 책을 가진 사람들 목록

// BookDetailView.vue

const fetchBookDetail = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    const response = await axios.get(
      `http://127.0.0.1:8000/api/v1/books/${route.params.isbn}/`, 
      { headers }
    );
    
    book.value = response.data;

    // 1. 내가 등록한 가격이 있다면 입력창 닫기 (이미 구현된 부분)
    if (book.value.my_price && book.value.my_price > 0) {
      sellingPrice.value = book.value.my_price;
      isPriceRegistered.value = true;
    }

    // 2. [핵심 수정] 이미 '구매 원해요'가 눌러진 상태라면 자동으로 이웃 목록 가져오기
    if (book.value.is_wish) {
      console.log("이미 관심 도서입니다. 이웃 목록을 자동으로 불러옵니다.");
      fetchOwners(); // <-- 여기서 함수를 실행해줘야 새로고침 없이 바로 보입니다!
    }

  } catch (err) {
    console.error("데이터 로드 실패:", err);
  }
};

// --- [추가] 가격 등록 함수 ---
const registerPrice = async () => {
  if (!sellingPrice.value) return alert("희망 가격을 입력해주세요.")
  const token = localStorage.getItem('access_token')
  try {
    // 동료분이 만들 백엔드 주소에 맞게 수정 필요
    await axios.post(`http://127.0.0.1:8000/api/v1/books/${book.value.isbn}/register-price/`, 
      { price: sellingPrice.value },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    alert("서책의 가치가 등록되었습니다.")
    isPriceRegistered.value = true
  } catch (err) {
    console.error("가격 등록 실패:", err)
    alert("등록 중 오류가 발생했습니다.")
  }
}
const editPrice = () => {
  isPriceRegistered.value = false
}
// --- [추가] 소장 중인 이웃 목록 가져오기 ---
const fetchOwners = async () => {
  try {
    // 1. 로컬 스토리지에서 토큰 가져오기
    const token = localStorage.getItem('access_token');
    
    // 2. headers 변수를 먼저 정의합니다. (에러 해결 핵심!)
    const headers = {};
    if (token && token !== 'null') {
      headers.Authorization = `Bearer ${token}`;
    }

    // 3. axios 요청 시 정의한 headers를 전달합니다.
    const res = await axios.get(
      `http://127.0.0.1:8000/api/v1/books/${book.value.isbn}/owners/`, 
      { headers } // 이제 headers가 정의되었으므로 에러가 나지 않습니다.
    );
    
    console.log("이웃 목록 로드 성공:", res.data);
    owners.value = res.data;
    
  } catch (err) {
    // 이제 ReferenceError 대신 실제 통신 에러가 있다면 잡힐 것입니다.
    console.error("소유자 목록 로드 실패:", err);
  }
};
// --- [추가] 채팅방으로 이동하는 함수 ---
const goToChat = async (owner) => {
  const token = localStorage.getItem('access_token')
  try {
    // 1. 여기서 백엔드에 '거래 생성' 요청을 보내 trade_id를 받아와야 함
    // const res = await axios.post(`http://127.0.0.1:8000/api/v1/trades/create/`, {
    //   seller_id: owner.id,
    //   isbn: book.value.isbn
    // }, { headers: { Authorization: `Bearer ${token}` } })
    
    // 2. 받은 trade_id로 이동 (지금은 임시 1번)
    router.push({ name: 'trade-chat', params: { trade_id: 1 } })
  } catch (err) {
    alert("대화방을 열 수 없습니다.")
  }
}

// --- [수정] 기존 toggleAction 함수 ---
const toggleAction = async (actionType) => {
  const token = localStorage.getItem('access_token')
  
  if (!token || token === 'null') {
    if (confirm("신분 확인이 필요한 서비스입니다. 페이지로 이동하시겠습니까?")) {
      router.push({ path: '/login', query: { redirect: route.fullPath } })
    }
    return; 
  }

  try {
    await axios.post(`http://127.0.0.1:8000/api/v1/books/${book.value.isbn}/action/${actionType}/`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (actionType === 'wish') {
      book.value.is_wish = !book.value.is_wish
      // [수정] 위시리스트 체크 시 소유자 목록을 뿅 하고 가져옴
      if (book.value.is_wish) fetchOwners()
    } else if (actionType === 'owned') {
      book.value.is_owned = !book.value.is_owned
    }
    
  } catch (err) {
    console.error("액션 실패:", err)
    if (err.response?.status === 401) {
      alert("세션이 만료되었습니다.")
      router.push('/login')
    }
  }
} 

onMounted(fetchBookDetail)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');

.detail-outer-container {
  min-height: 100vh; 
  display: flex;
  flex-direction: column;
  font-family: 'Hahmlet', serif;
}

.detail-outer-container.is-loading {
  justify-content: center;
  align-items: center;
}

.detail-container {
  flex: 1; 
  display: flex;
  gap: 40px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 60px 20px; 
  width: 100%;
  box-sizing: border-box;
}

.loading-state {
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f5ece0;
  border-top: 5px solid #81532e;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.loading-text {
  color: #81532e;
  font-size: 1.2rem;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.side-panel { flex: 0 0 300px; }

.cover-card {
  background: white;
  padding: 12px;
  border: 1px solid #d1b894;
  box-shadow: 10px 10px 20px rgba(0,0,0,0.05);
  margin-bottom: 25px;
}

.book-cover { width: 100%; display: block; }

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-classic {
  width: 100%; 
  box-sizing: border-box; 
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

/* 애니메이션 */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.4s ease-out;
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

/* 판매 가격 입력 카드 */
.selling-input-card {
  margin-top: 15px;
  padding: 15px;
  background: white;
  border: 1px solid #d1b894;
  text-align: left;
}
.input-label { font-size: 0.85rem; color: #81532e; margin-bottom: 10px; }
.input-group { display: flex; align-items: center; gap: 5px; }
.price-field { width: 100px; padding: 5px; border: 1px solid #ddd; }
.btn-save { background: #81532e; color: white; border: none; padding: 5px 10px; cursor: pointer; }

/* 소유자 목록 카드 */
.owner-list-card {
  margin-top: 15px;
  padding: 15px;
  background: #fdfaf5;
  border: 1px solid #d1b894;
  text-align: left;
}
.list-title { font-size: 0.95rem; color: #4a3423; margin-bottom: 12px; }
.owner-entry { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 8px 0;
  border-bottom: 1px solid #f5ece0;
}
.owner-name { font-size: 0.9rem; font-weight: 700; }
.owner-price { font-size: 0.9rem; color: #81532e; margin-left: 10px; }
.btn-tiny-chat { 
  font-size: 0.75rem; 
  padding: 4px 8px; 
  background: white; 
  border: 1px solid #81532e; 
  color: #81532e;
  cursor: pointer;
}
.btn-tiny-chat:hover { background: #81532e; color: white; }
.no-owner { font-size: 0.85rem; color: #999; }

/* 추가할 스타일 */
.main-info {
  display: flex;
  gap: 8px;
  align-items: baseline;
  margin-bottom: 4px;
}

.sub-info {
  font-size: 0.75rem;
  color: #888; /* 조금 흐리게 */
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-small {
  font-size: 0.7rem;
}

.owner-lib {
  font-style: normal;
}

.registered-price-view {
  text-align: center;
}

.price-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fdfaf5;
  padding: 10px;
  border-radius: 4px;
}

.final-price {
  font-size: 1.1rem;
  font-weight: 700;
  color: #81532e;
}

.btn-edit-small {
  background: transparent;
  border: 1px solid #d1b894;
  color: #d1b894;
  padding: 4px 8px;
  font-size: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-edit-small:hover {
  background: #f5ece0;
}
</style>