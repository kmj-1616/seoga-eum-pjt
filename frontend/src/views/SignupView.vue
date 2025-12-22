<template>
  <div class="signup-container">
    <h2>회원가입</h2>
    <form @submit.prevent="handleSignup" class="signup-form">
      <div class="input-group">
        <label>이메일</label>
        <input type="email" v-model="formData.email" required placeholder="example@email.com">
      </div>
      
      <div class="input-group">
        <label>비밀번호</label>
        <input type="password" v-model="formData.password" required>
      </div>

      <div class="input-group">
        <label>비밀번호 확인</label>
        <input type="password" v-model="formData.password_confirm" required>
      </div>

      <div class="input-group">
        <label>성함 (닉네임)</label>
        <input type="text" v-model="formData.nickname" required>
      </div>

      <div class="input-group">
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

      <div class="input-group">
        <label>성별</label>
        <div class="radio-group">
          <label><input type="radio" v-model="formData.gender" value="M" required> 남성</label>
          <label><input type="radio" v-model="formData.gender" value="F"> 여성</label>
          <label><input type="radio" v-model="formData.gender" value="O"> 기타</label>
        </div>
      </div>

      <div class="input-group">
        <label>관심 카테고리 (복수 선택)</label>
        <div class="checkbox-group">
          <label v-for="genre in genreOptions" :key="genre">
            <input type="checkbox" :value="genre" v-model="selectedGenres"> {{ genre }}
          </label>
        </div>
      </div>

      <button type="submit" class="signup-submit-btn">가입하기</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      // 1. formData 내부를 명확하게 다 적어줘야 에러가 안 납니다!
      formData: {
        email: '',
        password: '',
        password_confirm: '',
        nickname: '',
        age_group: '20s', // 기본값
        gender: '',
      },
      selectedGenres: [], // 체크박스 선택용
      selectedLibraries: ["국립중앙도서관"], // 전송 시 필요한 기본값
      genreOptions: [] // 백엔드에서 받아올 장르 목록
    }
  },
  mounted() {
    this.fetchCategories();
  },
  methods: {
    async fetchCategories() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/books/categories/');
        // 백엔드 데이터 구조에 따라 category.name 또는 category.name_ko 등을 확인하세요
        this.genreOptions = response.data.map(category => category.name);
      } catch (error) {
        console.log("카테고리 로딩 실패, 기본값을 사용합니다.");
        this.genreOptions = ['소설', '인문', '과학', '경제', '자기계발']; 
      }
    },
    async handleSignup() {
      // 비밀번호 체크
      if (this.formData.password !== this.formData.password_confirm) {
        alert("비밀번호가 일치하지 않습니다.");
        return;
      }

      // 백엔드 전송용 데이터 합치기
      const payload = {
        ...this.formData,
        preferred_genres: this.selectedGenres.join(','),
        favorite_libraries: this.selectedLibraries.join(',')
      };

      try {
        const response = await axios.post('http://127.0.0.1:8000/api/v1/users/register/', payload);
        alert("회원가입이 완료되었습니다!");
        
        // 토큰 저장 (동료분이 만든 API 구조)
        localStorage.setItem('access_token', response.data.tokens.access);
        
        this.$router.push('/');
      } catch (error) {
        console.error(error.response?.data);
        alert("에러 발생: " + JSON.stringify(error.response?.data));
      }
    }
  }
}
</script>

<style scoped>
/* 호준님의 기본 스타일 유지 */
.signup-container {
  max-width: 400px;
  margin: 60px auto;
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.input-group input[type="email"],
.input-group input[type="password"],
.input-group input[type="text"],
.input-group select {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

/* 성별 및 체크박스 정렬을 위한 스타일 추가 */
.radio-group, .checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 5px 0;
}

.radio-group label, .checkbox-group label {
  font-size: 14px;
  font-weight: normal;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.signup-submit-btn {
  background-color: #000;
  color: white;
  padding: 15px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.signup-submit-btn:hover {
  background-color: #333;
}
</style>