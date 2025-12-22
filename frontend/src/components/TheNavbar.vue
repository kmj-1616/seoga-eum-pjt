<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-logo" @click="goToHome">
        <img src="@/assets/logo.png" alt="서가이음 로고" class="logo-img" />
      </div>

      <ul class="navbar-center-menu">
        <li @click="goToHome" :class="{ active: $route.path === '/' }">
          <img src="@/assets/home-icon.png" alt="홈" class="menu-icon" />
          <span class="menu-text">홈</span>
        </li>
        <li @click="goToSearch">
          <img src="@/assets/search-icon.png" alt="검색" class="menu-icon" />
          <span class="menu-text">도서 검색</span>
        </li>
        <li @click="goToMypage">
          <img src="@/assets/user-icon.png" alt="마이페이지" class="menu-icon" />
          <span class="menu-text">마이페이지</span>
        </li>
      </ul>

      <div class="navbar-auth">
        <span @click="goToLogin" class="auth-item">로그인</span>
        <span @click="goToSignup" class="auth-item signup-box">회원가입</span>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'TheNavbar',
  methods: {
    goToHome() {
      this.$router.push('/')
    },
    goToLogin() {
      this.$router.push('/login')
    },
    goToSignup() {
      this.$router.push('/signup')
    }
  }
}
</script>

<style scoped>
.navbar {
  width: 100%;
  height: 80px; 
  background-color: white;
  border-bottom: 1px solid #1a0404;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
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
}
.logo-img {
  height: 40px;
  width: auto;
  display: block;
}

.menu-icon {
  width: 28px; 
  height: 28px;
  object-fit: contain; 
}

.navbar-center-menu {
  list-style: none;
  display: flex;
  gap: 60px;
  margin: 0;
  padding: 0;
}

.navbar-center-menu li {
  cursor: pointer;
  font-size: 18px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
}

.navbar-center-menu li.active {
  color: #81532e;
  font-weight: 600;
}

.navbar-auth {
  display: flex;
  align-items: center;
  gap: 20px;
}

.auth-item {
  cursor: pointer;
  font-size: 15px;
  color: #333;
}

.signup-box {
  background-color: #000;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
}

.auth-item:hover {
  opacity: 0.8;
}
</style>