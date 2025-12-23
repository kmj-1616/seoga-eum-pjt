<template>
  <div class="login-outer-container"> <div class="login-container">
      <h2>신분 확인</h2>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label>이메일 (전자우편)</label>
          <input 
            type="email" 
            v-model="loginData.email" 
            required 
            placeholder="example@email.com"
          >
        </div>
        
        <div class="input-group">
          <label>비밀번호 (암호)</label>
          <input 
            type="password" 
            v-model="loginData.password"
            required 
            placeholder="비밀번호를 입력하세요"
          >
        </div>

        <button type="submit" class="login-submit-btn">확인</button>

        <div class="login-helper">
          <span>명부에 없으신가요?</span>
          <router-link to="/signup">명부 등록 하러 가기</router-link>
        </div>
      </form>
    </div>
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
        localStorage.setItem('user_id', response.data.user.id);

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

        window.dispatchEvent(new Event('auth-change'));

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
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500;600;700&display=swap');

/* 전체 배경 */
.login-outer-container {
  background-color: #fdfaf5;
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png');
  min-height: calc(100vh - 85px); /* 네브바 높이 제외 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Hahmlet', serif;
}

.login-container {
  max-width: 420px;
  width: 90%;
  padding: 40px;
  background-color: white;
  border: 1px solid #d1b894; /* 고풍스러운 테두리 */
  box-shadow: 10px 10px 25px rgba(0,0,0,0.03);
}

h2 {
  margin-bottom: 35px;
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: #4a3423;
  letter-spacing: 2px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
}

.input-group label {
  font-size: 15px;
  font-weight: 600;
  color: #81532e;
}

.input-group input {
  padding: 14px;
  border: 1px solid #e5e7eb;
  background-color: #fdfcfb;
  font-size: 15px;
  font-family: 'Hahmlet', serif;
  transition: all 0.3s;
  outline: none;
}

.input-group input:focus {
  border-color: #81532e;
  background-color: white;
  box-shadow: 0 0 0 2px rgba(129, 83, 46, 0.1);
}

/* 플레이스홀더 폰트 적용 */
.input-group input::placeholder {
  font-family: 'Hahmlet', serif;
  color: #c4b5a6;
  font-size: 14px;
}

.login-submit-btn {
  background-color: #81532e;
  color: #fdfaf5;
  padding: 16px;
  border: 1px solid #4a3423;
  font-size: 17px;
  font-weight: 600;
  font-family: 'Hahmlet', serif;
  cursor: pointer;
  transition: 0.3s;
  margin-top: 10px;
}

.login-submit-btn:hover {
  background-color: #4a3423;
}

.login-helper {
  margin-top: 20px;
  font-size: 14px;
  color: #6d5d50;
  text-align: center;
}

.login-helper a {
  margin-left: 10px;
  color: #81532e;
  text-decoration: none;
  font-weight: 700;
  border-bottom: 1px solid #81532e;
  padding-bottom: 2px;
}

.login-helper a:hover {
  color: #4a3423;
  border-color: #4a3423;
}
</style>