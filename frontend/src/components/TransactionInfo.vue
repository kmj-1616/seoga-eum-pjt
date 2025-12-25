<template>
  <div class="transaction-panel">
    <div class="book-summary-box">
      <div class="book-text-group">
        <p class="book-author">{{ bookAuthor }}</p>
        <h4 class="book-title">{{ bookTitle }}</h4>
      </div>
      <div class="book-price-row">
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

    <div v-if="pendingRequest" class="status-request-section">
      <div class="request-box">
        <template v-if="isActionRequired">
          <p class="request-text">
            <strong>{{ pendingRequest.requester_nickname }}</strong> 님이
            <strong>{{ getStatusLabel(pendingRequest.new_status) }}</strong>를 요청했습니다.
          </p>
          <div class="request-buttons">
            <button class="btn-reject" @click="rejectRequest">거절</button>
            <button class="btn-accept" @click="acceptRequest">수락</button>
          </div>
        </template>
        <template v-else>
          <p class="request-text" style="text-align: center; color: #856404; margin: 0;">
            상대방의 <strong>{{ getStatusLabel(pendingRequest.new_status) }}</strong> 승인을 기다리는 중...
          </p>
        </template>
      </div>
    </div>

    <div v-if="userRole === 'seller' && status === 'LIBRARY_STORED'" class="location-edit-section">
      <h5 class="section-subtitle">📍 거래 장소 설정</h5>
      <div class="location-form">
        <div class="library-search-container">
          <div class="search-input-wrapper">
            <input 
              type="text" 
              v-model="locationInput" 
              @input="searchLibraries" 
              placeholder="도서관 검색" 
              class="location-search-input" 
            />
            <ul v-if="librarySearchResults.length > 0" class="search-dropdown">
              <li v-for="lib in librarySearchResults" :key="lib.lib_code" @click="selectLibrary(lib)">
                <span class="lib-name">{{ lib.lib_name }}</span>
                <span class="lib-addr">{{ lib.address }}</span>
              </li>
            </ul>
          </div>
          <input v-model="lockerNumberInput" type="text" placeholder="함 번호" class="locker-input" />
        </div>
        <button class="btn-save-location" @click="saveLocation" :disabled="isLoading">
          {{ isLoading ? '저장 중...' : '거래 장소 저장' }}
        </button>
      </div>
    </div>

    <div v-if="status === 'LIBRARY_STORED' && props.libraryName" class="location-info-section">
      <h5 class="section-subtitle">📍 거래 장소</h5>
      <div class="library-card">
        <strong class="lib-name">{{ displayLocation }}</strong>
        <p class="lib-address">{{ libraryAddress }}</p>
        <div class="locker-tag-row">
          <span class="locker-label">보관함</span>
          <span class="locker-id">{{ displayLockerNumber }}</span>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button class="request-btn" v-if="userRole === 'buyer' && status === 'APPROVED' && !pendingRequest" @click="requestStatusChange('LIBRARY_STORED')">📦 도서관 보관 요청하기</button>
      <button class="confirm-btn" v-if="userRole === 'buyer' && status === 'LIBRARY_STORED' && !pendingRequest" @click="confirmReceipt">✓ 수령 완료</button>

      <div v-if="!pendingRequest && !canTakeAction" class="status-notice">
        <span v-if="userRole === 'buyer' && status === 'REQUESTED'">판매자의 승인을 기다리는 중...</span>
        <span v-else-if="userRole === 'seller' && status === 'REQUESTED'">거래 요청을 확인해주세요.</span>
        <span v-else-if="userRole === 'seller' && status === 'APPROVED'">구매자의 보관 요청 대기 중...</span>
        <span v-else-if="status === 'LIBRARY_STORED'">구매자가 수령을 대기 중입니다.</span>
        <span v-else-if="status === 'COMPLETED'">거래가 완료되었습니다.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
  bookTitle: { type: String, default: '' },
  bookAuthor: { type: String, default: '' },
  bookPrice: { type: Number, default: 0 },
  status: { type: String, default: 'REQUESTED' },
  userRole: { type: String, default: 'buyer' },
  tradeId: { type: [Number, String], required: true },
  libraryName: { type: String, default: '' },
  libraryAddress: { type: String, default: '' },
  lockerNumber: { type: String, default: '' },
  pendingStatusRequest: { type: Object, default: null }
});

const emit = defineEmits(['confirm-receipt', 'status-changed']);

const pendingRequest = ref(props.pendingStatusRequest);
const isLoading = ref(false);
const locationInput = ref('');
const lockerNumberInput = ref('');
const selectedLibraryAddress = ref('');
const librarySearchResults = ref([]);

onMounted(() => {
  if (props.libraryName) locationInput.value = props.libraryName;
  if (props.lockerNumber) lockerNumberInput.value = props.lockerNumber;
});

watch(() => props.pendingStatusRequest, (newVal) => { pendingRequest.value = newVal; }, { deep: true });
watch(() => props.libraryName, (val) => { if (val) locationInput.value = val; });
watch(() => props.lockerNumber, (val) => { if (val) lockerNumberInput.value = val; });

const steps = ['거래 요청', '거래 승인', '도서관 보관 요청', '구매자 수령', '거래 완료'];

const currentStep = computed(() => {
  const statusMap = { 'REQUESTED': 0, 'APPROVED': 1, 'LIBRARY_STORED': 2, 'COMPLETED': 4 };
  return statusMap[props.status] || 0;
});

const getStepStatus = (index) => {
  if (index < currentStep.value) return 'completed';
  if (index === currentStep.value) return 'current';
  return 'pending';
};

const getStatusLabel = (status) => {
  const labels = { 'LIBRARY_STORED': '도서관 보관 중', 'COMPLETED': '거래 완료' };
  return labels[status] || status;
};

const canTakeAction = computed(() => {
  if (pendingRequest.value) return false;
  if (props.userRole === 'buyer' && (props.status === 'APPROVED' || props.status === 'LIBRARY_STORED')) return true;
  return false;
});

const searchLibraries = async () => {
  if (locationInput.value.length < 2) {
    librarySearchResults.value = [];
    return;
  }
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/books/libraries/', {
      params: { q: locationInput.value }
    });
    librarySearchResults.value = response.data.results || response.data;
  } catch (err) {
    console.error("도서관 검색 실패", err);
  }
};

const selectLibrary = (lib) => {
  locationInput.value = lib.lib_name;
  selectedLibraryAddress.value = lib.address;
  librarySearchResults.value = [];
};

const saveLocation = async () => {
  if (!locationInput.value || !lockerNumberInput.value) {
    alert('도서관과 보관함 번호를 입력해주세요.');
    return;
  }
  isLoading.value = true;
  const token = localStorage.getItem('access_token');
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/update-location/`,
      {
        location: locationInput.value,
        locker_number: lockerNumberInput.value,
        address: selectedLibraryAddress.value || props.libraryAddress 
      },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert('거래 장소가 저장되었습니다.');
    emit('status-changed', props.status); 
  } catch (err) {
    alert("저장 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

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
  } catch (err) {
    alert("요청 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

const currentUserId = computed(() => parseInt(localStorage.getItem('user_id')));
const isActionRequired = computed(() => {
  if (!pendingRequest.value) return false;
  return parseInt(pendingRequest.value.requester_id) !== currentUserId.value;
});

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
    pendingRequest.value = null;
    emit('status-changed', res.data.new_status);
  } catch (err) {
    alert("수락 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

const rejectRequest = async () => {
  if (!pendingRequest.value || isLoading.value) return;
  isLoading.value = true;
  const token = localStorage.getItem('access_token');
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request/${pendingRequest.value.id}/approve/`,
      { action: 'reject' },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    pendingRequest.value = null;
  } catch (err) {
    alert("거절 실패: " + (err.response?.data?.error || err.message));
  } finally {
    isLoading.value = false;
  }
};

const confirmReceipt = () => emit('confirm-receipt');
const displayLocation = computed(() => props.libraryName || '장소 정보 없음');
const displayLockerNumber = computed(() => props.lockerNumber || '-');
</script>

<style scoped>
/* 전체 패널 스크롤 설정 */
.transaction-panel { 
  text-align: left; 
  color: #333; 
  display: flex; 
  flex-direction: column; 
  gap: 0;
  max-height: 80vh; /* 부모 높이에 맞춰 스크롤 생성 */
  overflow-y: auto;
  padding-right: 4px;
}

/* 스크롤바 커스텀 */
.transaction-panel::-webkit-scrollbar { width: 4px; }
.transaction-panel::-webkit-scrollbar-thumb { background: #d1b894; border-radius: 10px; }

/* 도서 정보 압축 */
.book-summary-box { margin-bottom: 4px; }
.book-author { font-size: 11px; color: #999; margin: 0; }
.book-title { font-size: 15px; margin: 2px 0 6px 0; color: #2c2c2c; font-weight: 600; }
.book-price-row { display: flex; justify-content: flex-end; align-items: center; }
.price-value { font-size: 18px; font-weight: 700; color: #1976d2; }
.horizontal-divider { height: 1px; background: #f0f0f0; margin: 10px 0; }

/* 타임라인 압축 */
.section-subtitle { font-size: 13px; margin: 0 0 10px 0; font-weight: 600; color: #555; display: flex; align-items: center; gap: 6px; }
.timeline-container { display: flex; flex-direction: column; padding-left: 5px; }
.timeline-item { display: flex; gap: 10px; position: relative; padding-bottom: 12px; }
.timeline-item:last-child { padding-bottom: 0; }
.node-wrapper { display: flex; flex-direction: column; align-items: center; width: 18px; }
.status-node { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #eee; background: #fff; z-index: 2; display: flex; align-items: center; justify-content: center; font-size: 9px; }
.connector-line { width: 2px; flex-grow: 1; background: #f0f0f0; position: absolute; top: 18px; z-index: 1; }
.step-label { font-size: 12px; color: #bbb; padding-top: 1px; }

.timeline-item.completed .status-node { border-color: #81532e; background: #81532e; }
.timeline-item.completed .check-mark { color: #fff; font-weight: bold; }
.timeline-item.completed .step-label { color: #555; }
.timeline-item.completed .connector-line { background: #81532e; }
.timeline-item.current .status-node { border-color: #81532e; border-width: 2.5px; }
.timeline-item.current .step-label { color: #81532e; font-weight: 700; }

/* 요청 박스 */
.status-request-section { margin-top: 8px; padding: 10px; background: #fff9db; border: 1px solid #ffec99; border-radius: 8px; }
.request-text { font-size: 12px; margin-bottom: 8px; line-height: 1.4; }
.request-buttons { display: flex; gap: 6px; }
.btn-reject, .btn-accept { flex: 1; padding: 7px; font-size: 12px; border: none; border-radius: 4px; cursor: pointer; }
.btn-reject { background: #f1f3f5; }
.btn-accept { background: #81532e; color: #fff; }

/* 장소 섹션 압축 */
.location-edit-section, .location-info-section { margin-top: 12px; }
.location-form { display: flex; flex-direction: column; gap: 6px; }
.library-search-container { display: flex; gap: 6px; }
.location-search-input, .locker-input { padding: 9px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; }
.location-search-input { flex: 2; }
.locker-input { flex: 1; text-align: center; }
.btn-save-location { padding: 10px; background: #81532e; color: #fff; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 13px; }

.library-card { background: #fdfaf7; border: 1px solid #efeae5; border-radius: 8px; padding: 10px; }
.lib-name { font-size: 13px; color: #4a3423; display: block; margin-bottom: 2px; }
.lib-address { font-size: 11px; color: #888; margin: 0 0 8px 0; }
.locker-tag-row { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 5px 8px; border-radius: 4px; border: 1px solid #eee; }
.locker-label { font-size: 10px; color: #999; }
.locker-id { font-size: 13px; font-weight: 700; color: #81532e; }

/* 하단 버튼 영역 */
.action-buttons { margin-top: 12px; padding-bottom: 10px; }
.request-btn { width: 100%; padding: 12px; border: 1.5px solid #81532e; background: #fff; color: #81532e; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; }
.confirm-btn { width: 100%; padding: 12px; background: #81532e; color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 14px; }
.status-notice { padding: 9px; background: #f8f9fa; border-radius: 6px; color: #888; font-size: 12px; text-align: center; border: 1px solid #eee; }
</style>