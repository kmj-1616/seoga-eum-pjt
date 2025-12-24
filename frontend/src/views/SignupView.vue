<template>
  <div class="signup-outer-container">
    <div class="signup-container">
      <h2>명부 작성</h2>
      <form @submit.prevent="handleSignup" class="signup-form">
        <div class="input-group">
          <label>이메일 (전자우편)</label>
          <input type="email" v-model="formData.email" required placeholder="example@email.com">
        </div>
        
        <div class="input-group">
          <label>비밀번호 (암호)</label>
          <input type="password" v-model="formData.password" required>
        </div>

        <div class="input-group">
          <label>비밀번호 확인</label>
          <input type="password" v-model="formData.password_confirm" required>
        </div>

        <div class="input-group">
          <label>닉네임 (별호)</label>
          <input type="text" v-model="formData.nickname" required>
        </div>

        <div class="input-group-row">
          <div class="input-group half">
            <label>연령대</label>
            <select v-model="formData.age_group">
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
              <label><input type="radio" v-model="formData.gender" value="M" required> 남성</label>
              <label><input type="radio" v-model="formData.gender" value="F"> 여성</label>
              <label><input type="radio" v-model="formData.gender" value="O"> 기타</label>
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
              @keydown.enter.prevent="searchLibraries"
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
            <label v-for="genre in genreOptions" :key="genre" class="chip-label">
              <input type="checkbox" :value="genre" v-model="selectedGenres"> {{ genre }}
            </label>
          </div>
        </div>

        <button type="submit" class="signup-submit-btn">작성 완료</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const formData = ref({
  email: '',
  password: '',
  password_confirm: '',
  nickname: '',
  age_group: '20s',
  gender: '',
})

const selectedGenres = ref([])
const genreOptions = ref([])

// 도서관 관련 상태
const librarySearchQuery = ref('')
const librarySearchResults = ref([])
const selectedLibraries = ref([])

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/categories/')
    genreOptions.value = response.data.map(category => category.name)
  } catch (error) {
    genreOptions.value = ['소설', '인문', '과학', '경제', '자기계발']
  }
})

// 도서관 검색 API 호출
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
  if (selectedLibraries.value.length >= 2) {
    alert("도서관은 최대 2개까지 선택 가능합니다.")
    return
  }
  if (!selectedLibraries.value.includes(libName)) {
    selectedLibraries.value.push(libName)
  }
  librarySearchQuery.value = ''
  librarySearchResults.value = []
}

const removeLibrary = (libName) => {
  selectedLibraries.value = selectedLibraries.value.filter(l => l !== libName)
}

const handleSignup = async () => {
  // 1. 유효성 검사 (비밀번호, 도서관)
  if (formData.value.password !== formData.value.password_confirm) {
    alert("비밀번호가 일치하지 않습니다.");
    return;
  }
  if (selectedLibraries.value.length === 0) {
    alert("최소 하나 이상의 도서관을 선택해야 합니다.");
    return;
  }

  const payload = {
    ...formData.value,
    preferred_genres: selectedGenres.value.join(','),
    favorite_libraries: selectedLibraries.value.join(',')
  };

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/users/register/', payload);
    
    // 2. 필수 데이터 저장 (닉네임이 빠지면 홈에서 '사용자'로 보임)
    localStorage.setItem('access_token', response.data.tokens.access);
    localStorage.setItem('refresh_token', response.data.tokens.refresh);
    localStorage.setItem('user_nickname', response.data.user.nickname); 

    // 3. 위치 정보 처리 (LoginView와 동일한 로직 적용)
    const DEFAULT_LAT = 37.5012;
    const DEFAULT_LON = 127.0395;

    if (navigator.geolocation) {
      await new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            localStorage.setItem('user_lat', pos.coords.latitude);
            localStorage.setItem('user_lon', pos.coords.longitude);
            resolve();
          },
          (err) => {
            localStorage.setItem('user_lat', DEFAULT_LAT);
            localStorage.setItem('user_lon', DEFAULT_LON);
            resolve();
          },
          { timeout: 5000 }
        );
      });
    } else {
      localStorage.setItem('user_lat', DEFAULT_LAT);
      localStorage.setItem('user_lon', DEFAULT_LON);
    }

    // 4. 상태 변경 알림 (네브바/홈 화면 갱신용)
    window.dispatchEvent(new Event('auth-change'));

    alert(`${response.data.user.nickname}님, 서가이음 명부 등록을 환영합니다!`);
    router.push('/');
    
  } catch (error) {
    console.error(error.response?.data);
    alert("가입 실패: " + JSON.stringify(error.response?.data));
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500;600;700&display=swap');

.signup-outer-container {
  background-color: #fdfaf5;
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png');
  min-height: 100vh;
  padding: 60px 0;
  font-family: 'Hahmlet', serif;
}

.signup-container {
  max-width: 500px;
  width: 90%;
  margin: 0 auto;
  padding: 40px;
  background-color: white;
  border: 1px solid #d1b894;
  box-shadow: 10px 10px 25px rgba(0,0,0,0.03);
}

h2 { text-align: center; color: #4a3423; margin-bottom: 30px; letter-spacing: 2px; }

.signup-form { display: flex; flex-direction: column; gap: 20px; }

.input-group { display: flex; flex-direction: column; gap: 8px; text-align: left; }
.input-group label { font-size: 14px; font-weight: 600; color: #81532e; }

.input-group input, .input-group select {
  padding: 12px;
  border: 1px solid #e5e7eb;
  background-color: #fdfcfb;
  font-family: 'Hahmlet', serif;
  outline: none;
}

.input-group-row { display: flex; gap: 15px; }
.half { flex: 1; }

/* 도서관 검색창 및 결과 스타일 */
.library-search-box {
  position: relative;
  width: 100%; /* 부모 너비에 맞춤 */
}

/* 도서관 검색 입력창 */
.library-search-box input {
  width: 100%; /* 너비 꽉 채우기 */
  box-sizing: border-box; /* 패딩 포함 너비 계산 */
  padding: 12px;
  border: 1px solid #e5e7eb;
  background-color: #fdfcfb;
  font-size: 15px;
  font-family: 'Hahmlet', serif;
  outline: none;
  transition: 0.3s;
}

.library-search-box input:focus {
  border-color: #81532e;
  background-color: white;
}

/* 검색 결과 목록 (너비 자동 일치) */
.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0; /* 좌우 끝을 부모에 맞춤 */
  background: white;
  border: 1px solid #d1b894;
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  padding: 0;
  margin: 0;
}

.search-results li {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f5ece0;
  font-size: 14px;
}
.search-results li:hover { background-color: #fdfaf5; color: #81532e; }
.lib-addr { font-size: 12px; color: #999; margin-left: 8px; }

/* 선택된 도서관 칩 */
.selected-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 5px; }
.chip {
  background: #81532e;
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.remove-chip {
  background: none; border: none; color: white; cursor: pointer; font-weight: bold;
}

.checkbox-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip-label { 
  font-size: 13px; padding: 6px 12px; background: #fdfaf5; 
  border: 1px solid #f5ece0; border-radius: 4px; cursor: pointer; 
}

.signup-submit-btn {
  background-color: #81532e; color: #fdfaf5; padding: 16px;
  border: 1px solid #4a3423; font-weight: 600; cursor: pointer; margin-top: 10px;
  font-family: 'Hahmlet', serif;
}
.signup-submit-btn:hover { background-color: #4a3423; }
</style>