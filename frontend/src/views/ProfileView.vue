<template>
  <div class="profile-outer-container">
    <div class="profile-container" v-if="userInfo">
    <div v-if="isEditModalOpen" class="modal-overlay">
      <div class="signup-container modal-content">
        <h2>명부 수정</h2>
        <div class="signup-form">
          <div class="input-group">
            <label>이메일 (전자우편)</label>
            <input type="email" v-model="editForm.email" placeholder="example@email.com">
          </div>

          <div class="input-group">
            <label>닉네임 (별호)</label>
            <input type="text" v-model="editForm.nickname">
          </div>

          <div class="input-group-row">
            <div class="input-group half">
              <label>연령대</label>
              <select v-model="editForm.age_group">
                <option value="10s">10대</option>
                <option value="20s">20대</option>
                <option value="30s">30대</option>
                <option value="40s">40대</option>
                <option value="50s">50대</option>
                <option value="60s+">60대 이상</option>
              </select>
            </div>
            <div class="input-group half">
              <label>성별</label>
              <div class="radio-group">
                <label><input type="radio" v-model="editForm.gender" value="M"> 남성</label>
                <label><input type="radio" v-model="editForm.gender" value="F"> 여성</label>
                <label><input type="radio" v-model="editForm.gender" value="O"> 기타</label>
              </div>
            </div>
          </div>

          <div class="input-group">
            <label>자주 이용하는 도서관 (최대 2개)</label>
            <div class="library-search-box">
              <input 
                type="text" 
                v-model="librarySearchQuery" 
                @input="searchLibraries" 
                placeholder="도서관 이름을 입력하세요..."
                :disabled="selectedLibraries.length >= 2"
              >
              <ul v-if="librarySearchResults.length > 0" class="search-results">
                <li v-for="lib in librarySearchResults" :key="lib.lib_code" @click="selectLibrary(lib.lib_name)">
                  {{ lib.lib_name }} <span class="lib-addr">{{ lib.address }}</span>
                </li>
              </ul>
            </div>
            <div class="selected-chips">
              <span v-for="lib in selectedLibraries" :key="lib" class="chip">
                {{ lib }}
                <button type="button" @click="removeLibrary(lib)" class="remove-chip">&times;</button>
              </span>
            </div>
          </div>

          <div class="input-group">
            <label>관심 분야 (복수 선택)</label>
            <div class="checkbox-group">
              <label v-for="genre in genreOptions" :key="genre" class="chip-label" :class="{ active: selectedGenres.includes(genre) }">
                <input type="checkbox" :value="genre" v-model="selectedGenres" hidden> {{ genre }}
              </label>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="isEditModalOpen = false">취소</button>
            <button class="signup-submit-btn" @click="handleProfileUpdate">수정 완료</button>
          </div>
        </div>
      </div>
    </div>

    <header class="profile-header">
      <h1 class="main-title">내 서재</h1>
      <p class="sub-title">나의 독서 활동과 정보를 관리하세요.</p>
    </header>

    <div class="user-card">
      <div class="user-content">
        <div class="user-info-main">
          <h2 class="user-name">{{ userInfo.nickname || userInfo.username }}</h2>
          <button class="edit-info-btn-inline" @click="openEditModal">정보 수정</button>
        </div>  
        <p class="user-email">{{ userInfo.email }}</p>
        
        <div class="preference-tags">
          <span class="p-tag gray">{{ ageGroupMap[userInfo.age_group] || userInfo.age_group }}</span>
          <span class="p-tag gray">{{ userInfo.gender === 'M' ? '남성' : userInfo.gender === 'F' ? '여성' : '기타' }}</span>
          <span v-for="tag in (userInfo.preferred_genres ? userInfo.preferred_genres.split(',') : [])" :key="tag" class="p-tag">
            {{ tag }}
          </span>
        </div>
        <p class="user-location"><img src="@/assets/home-icon.png" alt="도서관" class="lib-icon" /> {{ userInfo.favorite_libraries || '등록된 도서관이 없습니다.' }}</p>
      </div>
    </div>

    <nav class="info-tabs">
      <button v-for="tab in tabs" :key="tab.id" :class="['tab-item', { active: currentTab === tab.id }]" @click="currentTab = tab.id">
        {{ tab.icon }} {{ tab.name }}
      </button>
    </nav>

    <section class="shelf-section" v-if="currentTab === 'shelf'">
      <h3 class="section-title">소장 중인 서책</h3>
      <div v-if="ownedBooks.length > 0" class="shelf-grid">
        <div v-for="book in ownedBooks" :key="book.id" class="shelf-card">
          <div class="shelf-info">
            <h4 class="shelf-book-title" @click="$router.push(`/book/${book.isbn}`)" style="cursor: pointer;">
              {{ book.title }}
            </h4>
            <p class="shelf-book-author">{{ book.author }}</p>
            <div class="shelf-badges">
              <span v-if="book.price" class="badge price">희망 판매가: {{ book.price.toLocaleString() }}원</span>
            </div>
          </div>
          <button class="sell-btn" @click="openPriceEditModal(book)">
            가치 수정
          </button>
        </div>
      </div>
      <div v-else class="empty-shelf">소장 중인 도서가 없습니다.</div>
    </section>

    <section class="shelf-section" v-else-if="currentTab === 'activity'">
      <h3 class="section-title">참여 중인 소통창</h3>
      <div v-if="myActivities.length > 0" class="shelf-grid">
        <div v-for="book in myActivities" :key="book.id" class="shelf-card">
          <div class="shelf-info">
            <h4 class="shelf-book-title" @click="$router.push(`/book/${book.isbn}`)" style="cursor: pointer;">
              {{ book.title }}
            </h4>
            <p class="shelf-book-author">{{ book.author }}</p>
            <div class="shelf-badges">
              <span class="badge" style="background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;">참여 중</span>
            </div>
          </div>
          <button class="sell-btn" @click="$router.push(`/community/${book.isbn}`)">
            입장하기
          </button>
        </div>
      </div>
      <div v-else class="empty-shelf">아직 참여한 소통창이 없습니다.</div>
    </section>

<section v-else class="empty-state">해당 서비스는 준비 중입니다.</section>
  </div>

  <div v-else class="loading-state">
    <p>신분 확인이 필요합니다.</p>
  </div>

  <div v-if="isPriceEditModalOpen" class="modal-overlay">
  <div class="signup-container modal-content" style="max-width: 350px;">
    <h2>가치 수정</h2>
    <p style="font-size: 14px; color: #666; margin-bottom: 20px; text-align: center;">
      '{{ selectedBookForEdit?.title }}'의<br>희망 판매 가격을 입력해 주세요.
    </p>
    <div class="input-group">
      <div class="input-group-row" style="align-items: center; border-bottom: 1px solid #d1b894; padding-bottom: 5px;">
        <input 
          type="number" 
          v-model="newPrice" 
          style="flex: 1; border: none; font-size: 18px; text-align: right; outline: none; background: transparent;"
        >
        <span style="margin-left: 10px; font-weight: 600;">원</span>
      </div>
    </div>
    <div class="modal-footer" style="margin-top: 30px;">
      <button class="btn-cancel" @click="isPriceEditModalOpen = false">취소</button>
      <button class="signup-submit-btn" @click="handlePriceUpdate">수정 완료</button>
    </div>
  </div>
</div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'

const router = useRouter()
const userInfo = ref(null)
const ownedBooks = ref([])
const currentTab = ref('shelf')
const myActivities = ref([])
const tabs = [
  { id: 'shelf', name: '나의 서가', icon: '📱' },
  { id: 'activity', name: '나의 소통', icon: '💭' },
  { id: 'history', name: '거래 내역', icon: '👜' }
]

// --- 수정 모달 및 도서관 검색 관련 상태 ---
const isEditModalOpen = ref(false)
const genreOptions = ref([])
const librarySearchQuery = ref('')
const librarySearchResults = ref([])
const selectedGenres = ref([])
const selectedLibraries = ref([])
const editForm = reactive({
  email: '',
  nickname: '',
  age_group: '',
  gender: ''
})

// 1. 프로필 & 도서 데이터 로드
const fetchUserProfile = async () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (!token) return
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/users/profile/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    userInfo.value = response.data
  } catch (error) { console.error("프로필 로드 실패:", error) }
}

const fetchMyOwnedBooks = async () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (!token) return
  
  try {
    // 1. 서버에 'owned=true' 파라미터를 명시하여 요청
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/', {
      params: { owned: 'true' },
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // 2. 서버가 보낸 데이터가 'results' 키 안에 들어있는지 확인
    const allData = response.data.results || response.data
    
    // 3. [수정된 로직] 
    // 서버가 'owned=true' 요청에 대해 이미 DB를 조회해서 필터링된 결과만 보내준다면,
    // 프론트엔드에서 굳이 'is_owned === true' 조건을 검사할 필요 없이 
    // 받은 데이터를 그대로 목록에 할당합니다.
    if (Array.isArray(allData)) {
      ownedBooks.value = allData; 
    } else {
      ownedBooks.value = [];
    }
  } catch (error) { 
    console.error("도서 로드 실패:", error) 
  }
}

const fetchMyActivities = async () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (!token) return
  
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/community/my-activities/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    myActivities.value = response.data
  } catch (error) {
    console.error("활동 데이터 로드 실패:", error)
  }
}

onMounted(async () => {
  await fetchUserProfile()
  await fetchMyOwnedBooks()
  await fetchMyActivities()
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/v1/books/categories/')
    genreOptions.value = res.data.map(c => c.name)
  } catch { genreOptions.value = ['소설', '인문', '과학', '경제', '자기계발'] }
})

// 2. 모달 제어 및 도서관 검색 함수
const openEditModal = () => {
  const u = userInfo.value
  editForm.email = u.email
  editForm.nickname = u.nickname
  editForm.age_group = u.age_group
  editForm.gender = u.gender
  selectedGenres.value = u.preferred_genres ? u.preferred_genres.split(',') : []
  selectedLibraries.value = u.favorite_libraries ? u.favorite_libraries.split(',') : []
  isEditModalOpen.value = true
}

const searchLibraries = async () => {
  if (librarySearchQuery.value.length < 2) {
    librarySearchResults.value = []
    return
  }
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/libraries/', {
      params: { q: librarySearchQuery.value }
    })
    
    if (response.data && response.data.results) {
      librarySearchResults.value = response.data.results
    } else {
      librarySearchResults.value = response.data 
    }
  } catch (err) {
    console.error("도서관 검색 실패", err)
    librarySearchResults.value = []
  }
}

const selectLibrary = (libName) => {
  if (selectedLibraries.value.length >= 2) { alert("최대 2개까지 선택 가능합니다."); return; }
  if (!selectedLibraries.value.includes(libName)) { selectedLibraries.value.push(libName) }
  librarySearchQuery.value = ''; librarySearchResults.value = []
}

const removeLibrary = (libName) => {
  selectedLibraries.value = selectedLibraries.value.filter(l => l !== libName)
}

const handleProfileUpdate = async () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  const payload = {
    ...editForm,
    preferred_genres: selectedGenres.value.join(','),
    favorite_libraries: selectedLibraries.value.join(',')
  }
  try {
    const res = await axios.patch('http://127.0.0.1:8000/api/v1/users/profile/update/', payload, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    userInfo.value = res.data       
    await fetchUserProfile()        

    isEditModalOpen.value = false
    alert("명부가 수정되었습니다.")
  } catch (err) { 
    alert("수정 실패: " + JSON.stringify(err.response?.data)) 
  }
}

const ageGroupMap = {
  '10s': '10대',
  '20s': '20대',
  '30s': '30대',
  '40s': '40대',
  '50s': '50대',
  '60s+': '60대 이상'
}

// --- 가격 수정 관련 상태 ---
const isPriceEditModalOpen = ref(false)
const selectedBookForEdit = ref(null)
const newPrice = ref(0)

// --- 가격 수정 모달 열기 ---
const openPriceEditModal = (book) => {
  selectedBookForEdit.value = book
  newPrice.value = book.price || 0 
  isPriceEditModalOpen.value = true
}

// 가격 수정 실행 (백엔드 register_price API 호출) 
const handlePriceUpdate = async () => {
  if (newPrice.value < 0) return alert("가격은 0원 이상이어야 합니다.")
  
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  try {
    await axios.post(`http://127.0.0.1:8000/api/v1/books/${selectedBookForEdit.value.isbn}/register-price/`, 
      { price: newPrice.value }, 
      { headers: { Authorization: `Bearer ${token}` } }
    )
    
    alert("서책의 가치가 수정되었습니다.")
    isPriceEditModalOpen.value = false
    await fetchMyOwnedBooks() // 수정 후 목록 새로고침
  } catch (err) {
    console.error("가격 수정 실패:", err)
    alert(err.response?.data?.error || "수정 중 오류가 발생했습니다.")
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500;600;700&display=swap');

.profile-outer-container {
  min-height: 100vh;
  padding: 60px 0;
  font-family: 'Hahmlet', serif;
}

.profile-container { 
  max-width: 1100px; margin: 0 auto; padding: 40px 20px; 
  font-family: 'Hahmlet', serif;
}

/* 모달 및 Signup 스타일 이식 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.signup-container {
  max-width: 500px; width: 90%; padding: 40px; background-color: white; 
  border: 1px solid #d1b894; box-shadow: 10px 10px 25px rgba(0,0,0,0.1);
}
.signup-container h2 { text-align: center; color: #4a3423; margin-bottom: 25px; }

/* 폼 요소 스타일 (SignupView와 동일) */
.signup-form { display: flex; flex-direction: column; gap: 18px; }
.input-group { display: flex; flex-direction: column; gap: 6px; text-align: left; }
.input-group label { font-size: 14px; font-weight: 600; color: #81532e; }
.input-group input, .input-group select {
  padding: 10px; border: 1px solid #e5e7eb; background-color: #fdfcfb; font-family: 'Hahmlet', serif; outline: none;
}
.input-group-row { display: flex; gap: 15px; }
.half { flex: 1; }
.radio-group { display: flex; gap: 10px; font-size: 14px; color: #4a3423; }

/* 도서관 검색 스타일 */
.library-search-box { position: relative; }
.search-results {
  position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #d1b894;
  max-height: 150px; overflow-y: auto; z-index: 100; padding: 0; margin: 0; list-style: none;
}
.search-results li { padding: 10px; cursor: pointer; border-bottom: 1px solid #f5ece0; font-size: 13px; }
.lib-addr { font-size: 11px; color: #999; margin-left: 5px; }
.selected-chips { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 5px; }
.chip { background: #81532e; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; display: flex; align-items: center; gap: 5px; }
.remove-chip { background: none; border: none; color: white; cursor: pointer; font-weight: bold; }

/* 관심 분야 칩 스타일 */
.checkbox-group { display: flex; flex-wrap: wrap; gap: 6px; }
.chip-label { 
  font-size: 12px; padding: 6px 12px; background: #fdfaf5; 
  border: 1px solid #f5ece0; border-radius: 4px; cursor: pointer; transition: 0.2s;
}
.chip-label.active { background: #81532e; color: white; border-color: #81532e; }

/* 버튼 스타일 */
.modal-footer { display: flex; gap: 10px; margin-top: 10px; }
.btn-cancel { flex: 1; padding: 14px; background: #eee; border: none; cursor: pointer; font-family: 'Hahmlet'; }
.signup-submit-btn {
  flex: 2; background-color: #81532e; color: #fdfaf5; padding: 14px;
  border: 1px solid #4a3423; font-weight: 600; cursor: pointer; font-family: 'Hahmlet';
}

/* 마이페이지 메인 UI 스타일 */
.user-card { display: flex; gap: 30px; padding: 30px; background: white; border: 1px solid #d1b894; margin-bottom: 30px; align-items: center; }
.edit-info-btn { padding: 8px 15px; border: 1px solid #d1b894; background: #fff; cursor: pointer; font-family: 'Hahmlet'; font-size: 14px; }
.p-tag { padding: 4px 12px; border: 1px solid #f5ece0; font-size: 14px; background: #fff; margin-right: 5px; }
.p-tag.gray { background: #f9f9f9; color: #888; }
.info-tabs { display: flex; background: #fdfaf5; border: 1px solid #f5ece0; margin-bottom: 25px; }
.tab-item { flex: 1; padding: 15px; border: none; background: transparent; cursor: pointer; font-family: 'Hahmlet'; font-weight: 600; font-size: 16px;}
.tab-item.active { background: #81532e; color: #fff; }
.shelf-card { display: flex; justify-content: space-between; align-items: center; padding: 20px; border: 1px solid #f5ece0; background: white; margin-bottom: 10px; }
.sell-btn {
  padding: 8px 15px;
  background-color: white;
  color: #81532e;
  border: 1px solid #81532e;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.sell-btn:hover {
  background-color: #81532e;
  color: white;
}
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.user-info-main {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 5px; 
}

.user-name {
  margin: 0;
  font-size: 24px;
  color: #4a3423;
}

.edit-info-btn-inline {
  padding: 4px 10px;
  font-size: 12px;
  background: transparent;
  border: 1px solid #d1b894;
}

.edit-info-btn-inline:hover {
  background-color: #81532e; 
  color: #ffffff;            
  border-color: #81532e;
  box-shadow: 0 2px 5px rgba(129, 83, 46, 0.2); 
}

.shelf-book-title {
  font-size: 19px;      
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;    
  transition: color 0.2s;
  line-height: 1.4;     
}

.shelf-book-title:hover {
  color: #81532e;  
  text-decoration: underline; 
}

.shelf-book-author {
  font-size: 15px;
  color: #777;
  margin-bottom: 10px;
}

.user-location {
  display: flex;
  align-items: center; 
  gap: 8px;           
  margin-top: 15px;
  color: #666;
  font-size: 16px;
}

.lib-icon {
  width: 24px;         
  height: 24px;
  object-fit: contain;
  filter: sepia(50%);
  display: block;      
}

.section-title {
  font-size: 22px;      
  font-weight: 700;
  color: #4a3423;
  margin-bottom: 20px;
  padding-left: 5px;
  border-left: 4px solid #81532e; 
  line-height: 1.2;
}

.empty-shelf {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 16px;
  background: #fdfcfb;
  border: 1px dashed #d1b894;
}
</style>