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
        
        // 1. 기본 인증 정보 저장
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);
        localStorage.setItem('user_nickname', response.data.user.nickname);

        // 2. 위치 정보 처리 (최초 로그인 시 권한 획득)
        const DEFAULT_LAT = 37.5012;
        const DEFAULT_LON = 127.0395;

        if (navigator.geolocation) {
          // 권한 요청 및 위치 획득 -> localStorage에 저장해서 요청할 때마다 실시간 좌표를 보냄 
          await new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
              (pos) => {
                localStorage.setItem('user_lat', pos.coords.latitude);
                localStorage.setItem('user_lon', pos.coords.longitude);
                resolve();
              },
              (err) => {
                // 거부하거나 오류 시 기본값(역삼) 저장
                localStorage.setItem('user_lat', DEFAULT_LAT);
                localStorage.setItem('user_lon', DEFAULT_LON);
                resolve();
              },
              { timeout: 5000 } // 너무 오래 대기하지 않도록 3초 설정
            );
          });
        } else {
          localStorage.setItem('user_lat', DEFAULT_LAT);
          localStorage.setItem('user_lon', DEFAULT_LON);
        }

        // 3. 페이지 이동
        const redirectPath = this.$route.query.redirect || '/';
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