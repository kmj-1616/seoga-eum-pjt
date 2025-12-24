<template>
  <div class="transaction-panel">
    <h3 class="panel-title">거래 정보</h3>

    <div class="book-summary-box">
      <div class="book-text-group">
        <h4 class="book-title">{{ bookTitle }}</h4>
        <p class="book-author">{{ bookAuthor }}</p>
      </div>
      <div class="book-price-row">
        <span class="grade-badge">{{ bookGrade }}</span>
        <span class="price-value">{{ Number(bookPrice).toLocaleString() }}원</span>
      </div>
    </div>

    <div class="horizontal-divider"></div>

    <div class="progress-section">
      <h5 class="section-subtitle">
        <span class="icon-box">📦</span> 거래 진행 상황
      </h5>
      <div class="timeline-container">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          :class="['timeline-item', getStepStatus(index)]"
        >
          <div class="node-wrapper">
            <div class="status-node">
              <span v-if="getStepStatus(index) === 'completed'" class="check-mark">✓</span>
              <span v-else-if="getStepStatus(index) === 'current'" class="clock-mark">🕒</span>
            </div>
            <div v-if="index < steps.length - 1" class="connector-line"></div>
          </div>
          
          <span class="step-label">{{ step }}</span>
        </div>
      </div>
    </div>

    <div v-if="currentStep >= 2" class="location-info-section">
      <h5 class="section-subtitle">
        <span class="icon-box">📍</span> 거래 장소
      </h5>
      <div class="library-card">
        <strong class="lib-name">{{ libraryName }}</strong>
        <p class="lib-address">{{ libraryAddress }}</p>
        <div class="locker-tag-row">
          <span class="locker-label">보관함 번호</span>
          <span class="locker-id">{{ lockerNumber }}</span>
        </div>
      </div>
    </div>

    <button 
      class="confirm-btn" 
      v-if="userRole === 'buyer'"
      :disabled="status !== 'LIBRARY_STORED'" 
      @click="$emit('confirm-receipt')"
    >
      {{ status === 'LIBRARY_STORED' ? '✓ 수령 완료' : '보관 대기 중' }}
    </button>

    <div v-else-if="userRole === 'seller'" class="seller-notice">
      {{ status === 'LIBRARY_STORED' ? '구매자가 수령하기를 기다리고 있습니다.' : '도서관 보관함에 책을 넣어주세요.' }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  bookTitle: { type: String, default: '데미안' },
  bookAuthor: { type: String, default: '헤르만 헤세' },
  bookPrice: { type: Number, default: 8000 },
  bookGrade: { type: String, default: '상급' },
  status: { type: String, default: 'LIBRARY_STORED' }, // API 상태값
  libraryName: { type: String, default: '강남도서관' },
  libraryAddress: { type: String, default: '서울시 강남구 개포로 235' },
  lockerNumber: { type: String, default: 'A-12' }
});

const emit = defineEmits(['confirm-receipt']);

// 단계 정의
const steps = ['거래 요청', '거래 승인', '도서관 보관 요청', '구매자 수령', '거래 완료'];

// 현재 상태를 숫자로 변환
const currentStep = computed(() => {
  const statusMap = {
    'REQUESTED': 0,
    'APPROVED': 1,
    'DELIVERING': 2,
    'LIBRARY_STORED': 3,
    'COMPLETED': 4
  };
  return statusMap[props.status] || 0;
});

// 스타일 클래스 판별
const getStepStatus = (index) => {
  if (index < currentStep.value) return 'completed';
  if (index === currentStep.value) return 'current';
  return 'pending';
};
</script>

<style scoped>
.transaction-panel {
  text-align: left;
  color: #333;
}

.panel-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
}

/* 도서 정보 */
.book-summary-box { margin-bottom: 16px; }
.book-title { font-size: 18px; margin: 0 0 4px 0; color: #000; }
.book-author { font-size: 14px; color: #777; margin: 0 0 12px 0; }
.book-price-row { display: flex; justify-content: space-between; align-items: center; }
.grade-badge { background: #f1f3f5; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #495057; }
.price-value { font-size: 22px; font-weight: 700; color: #3b5bdb; } /* 이미지의 파란색 */

.horizontal-divider { height: 1px; background: #eee; margin: 20px 0; }

/* 타임라인 */
.section-subtitle { font-size: 16px; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px; }
.timeline-container { display: flex; flex-direction: column; }

.timeline-item { display: flex; gap: 16px; position: relative; padding-bottom: 24px; }
.timeline-item:last-child { padding-bottom: 0; }

.node-wrapper { display: flex; flex-direction: column; align-items: center; width: 24px; }
.status-node {
  width: 24px; height: 24px; border-radius: 50%; border: 2px solid #ddd;
  background: #fff; z-index: 2; display: flex; align-items: center; justify-content: center;
}
.connector-line {
  width: 2px; flex-grow: 1; background: #eee; position: absolute; top: 24px; z-index: 1;
}

.step-label { font-size: 15px; color: #adb5bd; padding-top: 2px; }

/* 타임라인 상태별 색상 */
.timeline-item.completed .status-node { border-color: #51cf66; background: #fff; }
.timeline-item.completed .check-mark { color: #51cf66; font-weight: bold; }
.timeline-item.completed .step-label { color: #333; }
.timeline-item.completed .connector-line { background: #51cf66; }

.timeline-item.current .status-node { border-color: #3b5bdb; }
.timeline-item.current .clock-mark { font-size: 14px; }
.timeline-item.current .step-label { color: #3b5bdb; font-weight: 700; }

/* 거래 장소 */
.location-info-section { margin-top: 30px; }
.library-card { background: #f8f9fa; border-radius: 8px; padding: 16px; }
.lib-name { display: block; font-size: 16px; margin-bottom: 6px; }
.lib-address { font-size: 13px; color: #666; margin: 0 0 16px 0; }
.locker-tag-row { display: flex; align-items: center; gap: 10px; }
.locker-label { border: 1px solid #dee2e6; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #868e96; background: #fff; }
.locker-id { font-size: 16px; font-weight: 700; }

/* 수령 완료 버튼 */
.confirm-btn {
  width: 100%; margin-top: 30px; padding: 16px; border: none; border-radius: 8px;
  background: #1a1d23; color: #fff; font-size: 16px; font-weight: 700; cursor: pointer;
  transition: background 0.2s;
}
.confirm-btn:disabled { background: #e9ecef; color: #adb5bd; cursor: not-allowed; }
.confirm-btn:hover:not(:disabled) { background: #000; }
</style>