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
    goToMypage() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      // 로그인이 안 되어 있을 때
      if (confirm("신분 확인이 필요한 서비스입니다. 페이지로 이동하시겠습니까?")) {
        this.$router.push('/login');
      }
    } else {
      // 로그인 상태일 때 정상 이동
      this.$router.push('/profile');
    }
  },
  
  goToHome() { this.$router.push('/') },
  goToLogin() { this.$router.push('/login') },
  goToSignup() { this.$router.push('/signup') },
  goToSearch() { this.$router.push('/search') },
}
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');

.navbar {
  width: 100%;
  height: 85px; 
  background-color: #fdfaf5; 
  border-bottom: 2px solid #d1b894; 
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  font-family: 'Hahmlet', serif;
}

.navbar-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.navbar-logo { 
  cursor: pointer; 
  transition: transform 0.2s;
}
.navbar-logo:hover { transform: scale(1.02); }

.logo-img { height: 45px; width: auto; display: block; }

/* 중앙 메뉴 */
.navbar-center-menu { 
  list-style: none; 
  display: flex; 
  gap: 50px; 
  margin: 0; 
  padding: 0; 
}

.navbar-center-menu li { 
  cursor: pointer; 
  font-size: 18px; 
  color: #5a4a3a; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  transition: 0.3s;
  font-family: 'Hahmlet', serif;
}

.navbar-center-menu li:hover { color: #81532e; }

.navbar-center-menu li.active { 
  color: #81532e; 
  font-weight: 700; 
  border-bottom: 2px solid #81532e;
  padding-bottom: 4px;
}

.menu-icon { width: 24px; height: 24px; object-fit: contain; filter: sepia(50%); }

/* 우측 인증 섹션 */
.navbar-auth { 
  display: flex; 
  align-items: center; 
  gap: 15px; 
  font-family: 'Hahmlet', serif;
}

.auth-item { 
  cursor: pointer; 
  font-size: 15px; 
  color: #4a3423; 
  transition: 0.2s;
}

/* 명부 등록 / 로그아웃 박스 (Classic 스타일) */
.signup-box, .logout-box { 
  border: 1px solid #81532e;
  padding: 8px 18px; 
  border-radius: 4px; 
  font-weight: 600; 
  transition: 0.3s;
}

.signup-box { 
  background-color: #81532e; 
  color: #fdfaf5 !important; 
}

.signup-box:hover { 
  background-color: #4a3423; 
}

.logout-box { 
  background-color: white; 
  color: #81532e; 
}

.logout-box:hover { 
  background-color: #f5ece0; 
}

.user-name {
  font-weight: 700;
  color: #81532e;
  font-size: 16px;
  margin-right: 5px;
}

.auth-item:hover { opacity: 0.8; }
</style>