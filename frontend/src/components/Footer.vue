<template>
  <footer class="footer-container">
    <div class="footer-content">
      <div class="footer-brand">
        <h2 class="footer-logo">서가이음</h2>
        <p class="footer-motto">서책으로 사람을 잇다, 문장의 인연을 소중히 여깁니다.</p>
        <p class="footer-motto">서가를 넘나들며 지식과 인연이 만나는 곳.</p>
      </div>

      <div class="footer-links">
        <h4>서가이음의 서비스</h4>
        <ul>
          <li>대문</li>
          <li>서가 둘러보기</li>
          <li>활발한 독서 소통창</li>
          <li>중고 서책 거래</li>
        </ul>
      </div>

      <div class="footer-info">
        <h4>서가이음 정보</h4>
        <p>만든이: 권미정, 윤호준</p>
        <p>기술: Vue.js 3 & Django REST Framework</p>
        <p>문의: contact@seogaeum.ssafy.com</p>
        <p>주소: 서울특별시 강남구 테헤란로 (서가빌딩 7층)</p>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="divider"></div>
      <p>&copy; 2025 SEOGA-EUM. 모든 문장의 권리는 서가이음에 있습니다.</p>
    </div>
  </footer>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;700&display=swap');

.footer-container {
  background-color: #4a3423; /* 히어로 배너와 동일한 짙은 갈색 */
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png');
  background-blend-mode: overlay;
  color: #f5ece0;
  padding: 60px 20px 30px;
  font-family: 'Hahmlet', serif;
  border-top: 5px solid #81532e;
  margin-top: 100px; /* 본문과의 간격 */
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  gap: 50px;
}

/* 브랜드 섹션 */
.footer-logo {
  font-size: 32px;
  color: #F5DEB3;
  margin-bottom: 15px;
  letter-spacing: 3px;
}
.footer-motto {
  font-size: 15px;
  color: #d1b894;
  margin-bottom: 25px;
  line-height: 1.6;
}
.footer-social {
  display: flex;
  gap: 15px;
}
.social-icon {
  font-size: 20px;
  cursor: pointer;
  transition: opacity 0.3s;
}
.social-icon:hover {
  opacity: 0.7;
}

/* 중앙 & 우측 공통 */
h4 {
  font-size: 18px;
  color: #F5DEB3;
  margin-bottom: 20px;
  font-weight: 700;
}

.footer-links ul {
  list-style: none;
  padding: 0;
}
.footer-links li {
  margin-bottom: 12px;
  cursor: pointer;
  font-size: 15px;
  color: #d1b894;
  transition: color 0.3s;
}
.footer-links li:hover {
  color: #fff;
  text-decoration: underline;
}

.footer-info p {
  font-size: 14px;
  color: #d1b894;
  margin-bottom: 10px;
}

/* 하단 카피라이트 */
.footer-bottom {
  max-width: 1200px;
  margin: 40px auto 0;
  text-align: center;
}
.divider {
  height: 1px;
  background-color: rgba(211, 184, 148, 0.2);
  margin-bottom: 20px;
}
.footer-bottom p {
  font-size: 12px;
  color: #967979;
}

/* 반응형 처리 */
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .footer-social {
    justify-content: center;
  }
}
</style>