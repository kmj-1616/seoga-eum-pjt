<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-logo" @click="goToHome">
        <img src="@/assets/logo.png" alt="서가이음 로고" class="logo-img" />
      </div>

      <ul class="navbar-center-menu">
        <li @click="goToHome" :class="{ active: $route.path === '/' }">
          <img src="@/assets/home-icon.png" alt="마당" class="menu-icon" />
          <span class="menu-text">마당</span>
        </li>
        <li @click="goToSearch">
          <img src="@/assets/search-icon.png" alt="서적 탐색" class="menu-icon" />
          <span class="menu-text">서적 탐색</span>
        </li>
        <li @click="goToMypage">
          <img src="@/assets/user-icon.png" alt="내 서재" class="menu-icon" />
          <span class="menu-text">내 서재</span>
        </li>
      </ul>

      <div class="navbar-auth">
        <template v-if="!isLoggedIn">
          <span @click="goToLogin" class="auth-item">신분 확인</span>
          <span @click="goToSignup" class="auth-item signup-box">명부 등록</span>
        </template>
        
        <template v-else>
          <span class="auth-item user-name">{{ userNickname }}님</span>
          <span @click="handleLogout" class="auth-item logout-box">로그아웃</span>
        </template>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'TheNavbar',
  data() {
    return {
      isLoggedIn: false,
      userNickname: ''
    }
  },
  // 컴포넌트가 로드될 때 실행
  mounted() {
    this.checkLoginStatus();
  },
  // 페이지 이동 시(라우트 변경) 로그인 상태를 매번 체크
  watch: {
    '$route'() {
      this.checkLoginStatus();
    }
  },
  methods: {
    checkLoginStatus() {
      const token = localStorage.getItem('access_token');
      this.isLoggedIn = !!token;
      this.userNickname = localStorage.getItem('user_nickname') || '사용자';
    },
    handleLogout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_nickname');
      this.isLoggedIn = false;
      this.userNickname = '';
      window.dispatchEvent(new CustomEvent('auth-change'));
      alert("로그아웃 되었습니다.");
      this.$router.push('/');
    },
    goToHome() { this.$router.push('/') },
    goToLogin() { this.$router.push('/login') },
    goToSignup() { this.$router.push('/signup') },
    goToSearch() { this.$router.push('/search') }, // 추가
    goToMypage() { this.$router.push('/profile') } // 추가
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');
/* 호준님이 짜놓으신 기존 CSS 그대로 사용 */
.navbar {
  width: 100%;
  height: 80px; 
  background-color: white;
  /* 구분선 */
  /* border-bottom: 1px solid #1a0404; */
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  font-weight: 750;
  font-family: 'Nanum Myeongjo', serif;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

/* ... (기존 CSS들) ... */

/* 로그아웃 버튼도 회원가입 박스처럼 예쁘게 보이게 추가 스타일 */
.logout-box {
  background-color: #f4f4f4; /* 회원가입이랑 차이를 주기 위해 연한 회색 */
  color: #333;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
}

.user-name {
  font-weight: 600;
  color: #81532e; /* 포인트 컬러 */
}

/* 호준님의 나머지 스타일들 유지... */
.navbar-logo { cursor: pointer; }
.logo-img { height: 40px; width: auto; display: block; }
.menu-icon { width: 28px; height: 28px; object-fit: contain; }
.navbar-center-menu { list-style: none; display: flex; gap: 60px; margin: 0; padding: 0; }
.navbar-center-menu li { cursor: pointer; font-size: 18px; color: #666; display: flex; align-items: center; gap: 5px; }
.navbar-center-menu li.active { color: #81532e; font-weight: 600; }
.navbar-auth { display: flex; align-items: center; gap: 20px; }
.auth-item { cursor: pointer; font-size: 15px; color: #333; }
.signup-box { background-color: #000; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 500; }
.auth-item:hover { opacity: 0.8; }
</style>