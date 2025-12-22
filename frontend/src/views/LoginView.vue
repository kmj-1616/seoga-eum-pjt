<template>
  <div class="login-container">
    <h2>신분 확인</h2>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="input-group">
        <label>이메일</label>
        <input 
          type="email" 
          v-model="loginData.email" 
          required 
          placeholder="example@email.com"
        >
      </div>
      
      <div class="input-group">
        <label>비밀번호</label>
        <input 
          type="password" 
          v-model="loginData.password"
          required 
          placeholder="비밀번호를 입력하세요"
        >
      </div>

      <button type="submit" class="login-submit-btn">신분 확인</button>

      <div class="login-helper">
        <span>명부에 없으신가요?</span>
        <router-link to="/signup">명부 등록 하러 가기</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginView',
  data() {
    return {
      loginData: {
        email: '',
        password: ''
      }
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/v1/users/login/', this.loginData);
        
        // 1. 토큰 저장
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);
        localStorage.setItem('user_nickname', response.data.user.nickname);

        // 2. 리다이렉트 경로 결정
        // 쿼리에 redirect 정보가 있으면 거기로 가고, 없으면 홈('/')으로 보냅니다.
        const redirectPath = this.$route.query.redirect || '/';

        // 3. 페이지 이동 및 상태 반영
        // 상태 반영을 위해 네비바가 Pinia 등을 안 쓴다면 window.location.href가 가장 확실합니다.
        // 만약 Pinia/Vuex를 사용 중이라면 this.$router.push(redirectPath)를 쓰세요.
        window.location.href = redirectPath; 

      } catch (error) {
        console.error("로그인 에러:", error.response?.data);
        alert("로그인 실패: " + (error.response?.data?.detail || "이메일 또는 비밀번호를 확인하세요."));
      }
    }
  }
}
</script>

<style scoped>
/* SignupView와 동일한 스타일 적용 */
.login-container {
  max-width: 400px;
  margin: 80px auto; /* 네비바 아래 여유 공간 */
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  background-color: white;
}

h2 {
  margin-bottom: 30px;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
}

.login-form {
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

.input-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.input-group input:focus {
  border-color: #000;
  outline: none;
}

.login-submit-btn {
  background-color: #000;
  color: white;
  padding: 15px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 10px;
}

.login-submit-btn:hover {
  background-color: #333;
}

.login-helper {
  margin-top: 15px;
  font-size: 13px;
  color: #666;
  text-align: center;
}

.login-helper a {
  margin-left: 8px;
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}
</style>