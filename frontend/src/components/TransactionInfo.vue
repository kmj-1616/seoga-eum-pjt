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
        <div v-for="(step, index) in steps" :key="index" :class="['timeline-item', getStepStatus(index)]">
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

    <!-- 상태 변경 요청 알림 -->
    <div v-if="pendingRequest" class="status-request-section">
      <div class="request-box">
        <p class="request-text">
          <strong>{{ pendingRequest.requester_nickname }}</strong>이(가)
          <strong>{{ getStatusLabel(pendingRequest.new_status) }}</strong>로 변경을 요청했습니다.
        </p>
        <div class="request-buttons">
          <button class="btn-reject" @click="rejectRequest">거절</button>
          <button class="btn-accept" @click="acceptRequest">수락</button>
        </div>
      </div>
    </div>

    <!-- 판매자가 보관 요청을 수락한 후에만 보관 장소 입력 허용 -->
    <div v-if="userRole === 'seller' && status === 'LIBRARY_STORED'" class="location-edit-section">
      <h5 class="section-subtitle">
        <span class="icon-box">📍</span> 거래 장소 설정
      </h5>
      <div class="location-form">
        <input v-model="locationInput" type="text" placeholder="거래 장소 (예: 강남도서관)" class="location-input" />
        <input v-model="lockerNumberInput" type="text" placeholder="보관함 번호 (예: A-12)" class="locker-input" />
        <button class="btn-save-location" @click="saveLocation" :disabled="isLoading">{{ isLoading ? '저장 중...' : '장소 저장' }}</button>
      </div>
    </div>

    <!-- 저장된 거래 장소 표시 (구매자에게 보이는 영역) -->
    <div v-if="currentStep >= 2" class="location-info-section">
      <h5 class="section-subtitle">
        <span class="icon-box">📍</span> 거래 장소
      </h5>
      <div class="library-card">
        <strong class="lib-name">{{ displayLocation }}</strong>
        <p class="lib-address">{{ libraryAddress }}</p>
        <div class="locker-tag-row">
          <span class="locker-label">보관함 번호</span>
          <span class="locker-id">{{ displayLockerNumber }}</span>
        </div>
      </div>
    </div>

    <!-- 상태별 액션 버튼 -->
    <div class="action-buttons">
      <!-- 구매자: APPROVED 상태에서 보관 요청 -->
      <button class="request-btn" v-if="userRole === 'buyer' && status === 'APPROVED' && !pendingRequest" @click="requestStatusChange('LIBRARY_STORED')">📦 도서관 보관을 요청하기</button>

      <!-- 구매자: LIBRARY_STORED 상태에서 수령 완료 -->
      <button class="confirm-btn" v-if="userRole === 'buyer' && status === 'LIBRARY_STORED' && !pendingRequest" @click="confirmReceipt">✓ 수령 완료</button>

      <!-- 상태별 알림 -->
      <div v-if="!pendingRequest && !canTakeAction" class="status-notice">
        <span v-if="userRole === 'buyer' && status === 'REQUESTED'">판매자의 승인을 기다리는 중입니다...</span>
        <span v-else-if="userRole === 'seller' && status === 'REQUESTED'">판매자: 거래 요청을 확인해주세요.</span>
        <span v-else-if="userRole === 'buyer' && status === 'APPROVED'">준비되면 도서관 보관을 요청하세요.</span>
        <span v-else-if="userRole === 'seller' && status === 'APPROVED'">구매자의 보관 요청을 기다리는 중입니다...</span>
        <span v-else-if="status === 'LIBRARY_STORED'">구매자가 수령을 대기 중입니다.</span>
        <span v-else-if="status === 'COMPLETED'">거래가 완료되었습니다.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import axios from 'axios';

// Props 정의
const props = defineProps({
  bookTitle: { type: String, default: '' },
  bookAuthor: { type: String, default: '' },
  bookPrice: { type: Number, default: 0 },
  bookGrade: { type: String, default: '상급' },
  status: { type: String, default: 'REQUESTED' },
  userRole: { type: String, default: 'buyer' },
  tradeId: { type: Number, required: true },
  libraryName: { type: String, default: '강남도서관' },
  libraryAddress: { type: String, default: '서울시 강남구 개포로 235' },
  lockerNumber: { type: String, default: 'A-12' },
  pendingStatusRequest: { type: Object, default: null }
});

const emit = defineEmits(['confirm-receipt', 'status-changed']);

// 상태 관리 - pendingStatusRequest를 watch하여 업데이트
const pendingRequest = ref(props.pendingStatusRequest);
const isLoading = ref(false);

// 거래 장소 입력 필드
const locationInput = ref('');
const lockerNumberInput = ref('');

// props.pendingStatusRequest 변경 감지
watch(() => props.pendingStatusRequest, (newVal) => {
  pendingRequest.value = newVal;
}, { deep: true });

// 입력 필드 초기화: 부모에서 전달된 값이 있으면 반영
watch(() => props.libraryName, (val) => {
  if (val) locationInput.value = val;
});
watch(() => props.lockerNumber, (val) => {
  if (val) lockerNumberInput.value = val;
});

// 단계 정의
const steps = ['거래 요청', '거래 승인', '도서관 보관 요청', '구매자 수령', '거래 완료'];

// 현재 상태를 숫자로 변환
const currentStep = computed(() => {
  const statusMap = {
    'REQUESTED': 0,
    'APPROVED': 1,
    'LIBRARY_STORED': 2,
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

// 상태 레이블
const getStatusLabel = (status) => {
  const labels = {
    'LIBRARY_STORED': '도서관 보관 중',
    'COMPLETED': '거래 완료'
  };
  return labels[status] || status;
};

// 액션 가능 여부
const canTakeAction = computed(() => {
  if (pendingRequest.value) return false;
  // 구매자: APPROVED 상태에서 보관 요청 가능
  if (props.userRole === 'buyer' && props.status === 'APPROVED') return true;
  // 구매자: LIBRARY_STORED 상태에서 수령 완료 가능
  if (props.userRole === 'buyer' && props.status === 'LIBRARY_STORED') return true;
  return false;
});

// 상태 변경 요청
const requestStatusChange = async (newStatus) => {
  if (isLoading.value) return;
  
  isLoading.value = true;
  const token = localStorage.getItem('access_token');
  
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request-status/`,
      { new_status: newStatus },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    pendingRequest.value = res.data;
    console.log("상태 변경 요청 생성:", res.data);
  } catch (err) {
    console.error("상태 변경 요청 실패:", err);
    alert("요청 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

// 요청 수락
const acceptRequest = async () => {
  if (!pendingRequest.value || isLoading.value) return;
  
  isLoading.value = true;
  const token = localStorage.getItem('access_token');
  
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request/${pendingRequest.value.id}/approve/`,
      { action: 'accept' },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    console.log("요청 수락:", res.data);
    pendingRequest.value = null;
    emit('status-changed', res.data.new_status);
  } catch (err) {
    console.error("요청 수락 실패:", err);
    alert("수락 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

// 요청 거절
const rejectRequest = async () => {
  if (!pendingRequest.value || isLoading.value) return;
  
  isLoading.value = true;
  const token = localStorage.getItem('access_token');
  
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request/${pendingRequest.value.id}/approve/`,
      { action: 'reject' },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    console.log("요청 거절:", res.data);
    pendingRequest.value = null;
  } catch (err) {
    console.error("요청 거절 실패:", err);
    alert("거절 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

// 수령 완료
const confirmReceipt = () => {
  emit('confirm-receipt');

// 거래 장소 저장
const saveLocation = async () => {
  if (!locationInput.value || !lockerNumberInput.value) {
    alert('거래 장소와 보관함 번호를 모두 입력해주세요.');
    return;
  }
  
  isLoading.value = true;
  const token = localStorage.getItem('access_token');
  
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/update-location/`,
      {
        location: locationInput.value,
        locker_number: lockerNumberInput.value
      },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    console.log("거래 장소 저장 완료:", res.data);
    alert('거래 장소가 저장되었습니다.');
    // props 업데이트를 위해 부모에 신호 전송
    emit('status-changed', props.status);
  } catch (err) {
    console.error("거래 장소 저장 실패:", err);
    alert("저장 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

// 표시할 거래 장소와 보관함 번호 (저장된 값 또는 입력값)
const displayLocation = computed(() => {
  if (locationInput.value) return locationInput.value;
  return props.libraryName || '강남도서관';
});

const displayLockerNumber = computed(() => {
  if (lockerNumberInput.value) return lockerNumberInput.value;
  return props.lockerNumber || 'A-12';
});
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

/* 상태 변경 요청 섹션 */
.status-request-section {
  margin-top: 20px;
  padding: 16px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
}

.request-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.request-text {
  margin: 0;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.request-buttons {
  display: flex;
  gap: 8px;
}

.btn-reject,
.btn-accept {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reject {
  background: #e9ecef;
  color: #495057;
}

.btn-reject:hover {
  background: #dee2e6;
}

.btn-accept {
  background: #51cf66;
  color: #fff;
}

.btn-accept:hover {
  background: #40c057;
}

/* 상태별 액션 버튼 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.request-btn {
  width: 100%;
  padding: 14px;
  border: 2px solid #81532e;
  background: #fff;
  color: #81532e;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.request-btn:hover {
  background: #f8f3f0;
}

.status-notice {
  padding: 12px;
  background: #e7f5ff;
  border-left: 4px solid #3b5bdb;
  border-radius: 4px;
  color: #1971c2;
  font-size: 14px;
  text-align: center;
}

/* 판매자용 거래 장소 편집 영역 */
.location-edit-section { margin-top: 16px; }
.location-form { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.location-input, .locker-input { padding: 8px 10px; border: 1px solid #e6e6e6; border-radius: 6px; width: 100%; }
.location-input { flex: 1 1 auto; }
.locker-input { width: 120px; }
.btn-save-location { background: #3b5bdb; color: #fff; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; }
.btn-save-location:disabled { opacity: 0.6; cursor: not-allowed; }

.location-info-section { margin-top: 16px; }
.library-card { background: #fff; padding: 12px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
.locker-tag-row { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.locker-label { font-size: 13px; color: #666; }
.locker-id { background: #f1f3f5; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
</style>