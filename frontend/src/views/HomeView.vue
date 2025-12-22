<template>
  <div class="home-container">
    <section class="hero-banner">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h2 class="hero-top-text">과거와 현재를 잇는 지혜의 서가</h2>
        <p class="hero-subtitle">당신만을 위한 고유한 책의 숨결을 느껴보세요</p>
        
        <div class="search-bar">
          <input type="text" placeholder="찾으시는 서책의 이름을 입력하십시오..." class="search-input">
          <button class="search-button">
            <img src="@/assets/search-icon.png" alt="검색" class="search-icon-img" />
          </button>
        </div>
      </div>
    </section>

    <section class="recommend-section">
      <div class="section-header">
        <span class="decoration-line"></span>
        <h3 class="section-title">오늘의 추천 서책</h3>
        <span class="decoration-line"></span>
      </div>
      <p class="section-desc">사용자의 취향에 맞춰 선별한 서적들입니다.</p>
      </section>
  </div>
</template>

<style scoped>
/* 구글에서 폰트 불러오기 */
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@400;700&display=swap');
.home-container {
  font-family: 'Nanum Myeongjo', serif;
  width: 100%;
  padding: 0;
  background-color: #fdfaf5;
  min-height: 100vh;
}

.hero-banner {
  padding-bottom: 60px;
  position: relative;
  background-color: #4a3423; 
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png'); 
  background-blend-mode: overlay;
  height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  border-bottom: 4px solid #81532e;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-top-text {
  font-family: 'Nanum Myeongjo', serif;
  font-size: 50px;
  font-weight: 400;
  letter-spacing: 5px;
  margin-bottom: 20px;
  color: #F5DEB3;
}

.hero-subtitle {
  font-family: 'Nanum Myeongjo', serif;
  font-size: 30px;
  margin-bottom: 40px;
  opacity: 1.2;
  font-weight: 300;
}

.search-bar {
  font-family: 'Nanum Myeongjo', serif;
  display: flex;
  background-color: rgba(255, 255, 255, 0.95);
  border: 2px solid #81532e;
  border-radius: 4px;
  width: 500px;
  margin: 0 auto;
  overflow: hidden;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
}

.search-input {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: transparent;
  font-size: 16px;
  outline: none;
  color: #4a3423;
}

.search-button {
  background-color: #81532e;
  border: none;
  padding: 0 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.3s;
}

.search-button:hover {
  background-color: #5d3b21;
}

.search-icon-img {
  width: 20px;
  filter: brightness(0) invert(1);
}

.recommend-section {
  max-width: 1200px;
  margin: 60px auto;
  padding: 0 20px;
  text-align: center;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 10px;
}

.decoration-line {
  height: 1px;
  width: 50px;
  background-color: #81532e;
}

.section-title {
  font-size: 28px;
  color: #4a3423;
  font-weight: 700;
}

.section-desc {
  color: #888;
  font-size: 16px;
}

.search-input::placeholder {
  font-family: 'Nanum Myeongjo', serif;
  letter-spacing: -0.5px; /* 글자를 살짝 모아서 정갈하게 */
  font-size: 15px;
  font-weight: 700;
}
</style>