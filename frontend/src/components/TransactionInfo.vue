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

    <div class="user-info-row">
      <div class="user-badge seller">
        <span class="role-tag">판매자</span>
        <span class="user-name">{{ sellerNickname || '익명' }}</span>
      </div>
      <div class="user-badge buyer">
        <span class="role-tag">구매자</span>
        <span class="user-name">{{ buyerNickname || '익명' }}</span>
      </div>
    </div>

    <div class="horizontal-divider"></div>

    <div class="progress-section">
      <h5 class="section-subtitle">📦 거래 진행 상황</h5>
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
          <p class="request-text waiting">상대방의 승인을 기다리는 중...</p>
        </template>
      </div>
    </div>

    <div v-if="userRole === 'seller' && status === 'LIBRARY_STORED'" class="location-edit-section">
      <h5 class="section-subtitle">📍 거래 장소 설정</h5>
      <div class="location-form">
        <div class="library-search-container">
          <div class="search-input-wrapper">
            <input type="text" v-model="locationInput" @input="searchLibraries" placeholder="도서관 검색" class="location-search-input" />
            <ul v-if="librarySearchResults.length > 0" class="search-dropdown">
              <li v-for="lib in librarySearchResults" :key="lib.lib_code" @click="selectLibrary(lib)">
                <span class="lib-name">{{ lib.lib_name }}</span>
                <span class="lib-addr">{{ lib.address }}</span>
              </li>
            </ul>
          </div>
          <input v-model="lockerNumberInput" type="text" placeholder="함 번호" class="locker-input" />
        </div>
        <button class="btn-save-location" @click="saveLocation" :disabled="isLoading">저장하기</button>
      </div>
    </div>

    <div v-if="status === 'LIBRARY_STORED' && libraryName" class="location-info-section">
      <h5 class="section-subtitle">📍 거래 장소</h5>
      <div class="library-card">
        <strong class="lib-name">{{ libraryName }}</strong>
        <p class="lib-address">{{ libraryAddress }}</p>
        <div class="locker-tag-row">
          <span class="locker-label">보관함</span>
          <span class="locker-id">{{ lockerNumber || '-' }}</span>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button class="request-btn" v-if="userRole === 'buyer' && status === 'APPROVED' && !pendingRequest" @click="requestStatusChange('LIBRARY_STORED')">📦 도서관 보관 요청</button>
      <button class="confirm-btn" v-if="userRole === 'buyer' && status === 'LIBRARY_STORED' && !pendingRequest" @click="confirmReceipt">✓ 수령 완료</button>

      <div v-if="!pendingRequest && !canTakeAction" class="status-notice">
        {{ getNoticeText }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
  bookTitle: String,
  bookAuthor: String,
  bookPrice: Number,
  status: String,
  userRole: String,
  tradeId: [Number, String],
  libraryName: String,
  libraryAddress: String,
  lockerNumber: String,
  pendingStatusRequest: Object,
  sellerNickname: String,
  buyerNickname: String
});

const emit = defineEmits(['confirm-receipt', 'status-changed']);

const pendingRequest = ref(props.pendingStatusRequest);
const isLoading = ref(false);
const locationInput = ref('');
const lockerNumberInput = ref('');
const selectedLibraryAddress = ref('');
const librarySearchResults = ref([]);

const steps = ['거래 요청', '거래 승인', '보관 요청', '수령 대기', '거래 완료'];

const currentStep = computed(() => {
  const map = { 'REQUESTED': 0, 'APPROVED': 1, 'LIBRARY_STORED': 3, 'COMPLETED': 4 };
  return map[props.status] ?? 0;
});

const getStepStatus = (index) => index < currentStep.value ? 'completed' : (index === currentStep.value ? 'current' : 'pending');

const getStatusLabel = (s) => ({ 'LIBRARY_STORED': '도서관 보관', 'COMPLETED': '거래 완료' }[s] || s);

const canTakeAction = computed(() => !pendingRequest.value && props.userRole === 'buyer' && (props.status === 'APPROVED' || props.status === 'LIBRARY_STORED'));

const getNoticeText = computed(() => {
  const { userRole, status } = props;
  
  if (status === 'COMPLETED') return '거래가 완료되었습니다.';
  
  if (userRole === 'seller') {
    if (status === 'REQUESTED') return '거래 요청을 확인해주세요.';
    if (status === 'APPROVED') return '구매자의 보관 요청 대기 중...';
    if (status === 'LIBRARY_STORED') return '구매자의 수령 대기 중...'; 
  } else if (userRole === 'buyer') {
    if (status === 'REQUESTED') return '판매자의 승인을 기다리는 중...';
  }
  
  return '상대방의 다음 단계를 기다리고 있습니다.';
});

const searchLibraries = async () => {
  if (locationInput.value.length < 2) return (librarySearchResults.value = []);
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/v1/books/libraries/', { params: { q: locationInput.value } });
    librarySearchResults.value = res.data.results || res.data;
  } catch (err) { console.error(err); }
};

const selectLibrary = (lib) => {
  locationInput.value = lib.lib_name;
  selectedLibraryAddress.value = lib.address;
  librarySearchResults.value = [];
};

const saveLocation = async () => {
  if (!locationInput.value || !lockerNumberInput.value) return alert('정보를 입력하세요.');
  isLoading.value = true;
  try {
    await axios.post(`http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/update-location/`, 
      { location: locationInput.value, locker_number: lockerNumberInput.value, address: selectedLibraryAddress.value || props.libraryAddress },
      { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
    );
    alert('저장되었습니다.');
    emit('status-changed');
  } catch (err) { alert("실패"); } finally { isLoading.value = false; }
};

const requestStatusChange = async (new_status) => {
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request-status/`, { new_status },
      { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
    );
    pendingRequest.value = res.data;
  } catch (err) { console.error(err); }
};

const isActionRequired = computed(() => pendingRequest.value && String(pendingRequest.value.requester_id) !== String(localStorage.getItem('user_id')));

const acceptRequest = async () => {
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request/${pendingRequest.value.id}/approve/`, { action: 'accept' },
      { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
    );
    pendingRequest.value = null;
    emit('status-changed', res.data.new_status);
  } catch (err) { console.error(err); }
};

const rejectRequest = async () => {
  try {
    await axios.post(`http://127.0.0.1:8000/api/v1/community/trade/${props.tradeId}/request/${pendingRequest.value.id}/approve/`, { action: 'reject' },
      { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
    );
    pendingRequest.value = null;
  } catch (err) { console.error(err); }
};

const confirmReceipt = () => emit('confirm-receipt');

watch(() => props.pendingStatusRequest, (v) => pendingRequest.value = v);
onMounted(() => {
  if (props.libraryName) locationInput.value = props.libraryName;
  if (props.lockerNumber) lockerNumberInput.value = props.lockerNumber;
});
</script>

<style scoped>
.transaction-panel { text-align: left; display: flex; flex-direction: column; gap: 0; }
.book-author { font-size: 11px; color: #999; margin: 0; }
.book-title { font-size: 15px; margin: 2px 0 6px 0; color: #2c2c2c; font-weight: 600; }
.price-value { font-size: 18px; font-weight: 700; color: #1976d2; }
.user-info-row { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
.user-badge { display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 6px; border: 1px solid #f5ece0; }
.user-badge.seller { background: #fdfaf5; }
.user-badge.buyer { background: #f0f7ff; border-color: #e1f0ff; }
.role-tag { font-size: 10px; font-weight: 700; padding: 2px 5px; border-radius: 3px; color: #fff; }
.seller .role-tag { background: #81532e; }
.buyer .role-tag { background: #1976d2; }
.user-name { font-size: 13px; font-weight: 500; color: #4a3423; }
.horizontal-divider { height: 1px; background: #f0f0f0; margin: 15px 0; }
.section-subtitle { font-size: 13px; margin: 0 0 10px 0; font-weight: 600; color: #555; }
.timeline-container { display: flex; flex-direction: column; padding-left: 5px; }
.timeline-item { display: flex; gap: 10px; position: relative; padding-bottom: 12px; }
.status-node { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #eee; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 9px; }
.connector-line { width: 2px; flex-grow: 1; background: #f0f0f0; position: absolute; top: 18px; left: 8px; bottom: 0; }
.timeline-item.completed .status-node { border-color: #81532e; background: #81532e; color: #fff; }
.timeline-item.completed .connector-line { background: #81532e; }
.timeline-item.current .status-node { border-color: #81532e; border-width: 2px; }
.step-label { font-size: 12px; color: #bbb; }
.timeline-item.current .step-label { color: #81532e; font-weight: 700; }
.timeline-item.completed .step-label { color: #555; }
.status-request-section { margin-top: 8px; padding: 12px; background: #fff9db; border-radius: 8px; border: 1px solid #ffec99; }
.request-text { font-size: 12px; margin-bottom: 8px; }
.request-text.waiting { text-align: center; color: #856404; margin: 0; }
.request-buttons { display: flex; gap: 6px; }
.btn-reject, .btn-accept { flex: 1; padding: 8px; font-size: 12px; border: none; border-radius: 4px; cursor: pointer; }
.btn-accept { background: #81532e; color: #fff; }
.location-edit-section { margin-top: 15px; }
.library-search-container { display: flex; gap: 5px; margin-bottom: 8px; }
.search-input-wrapper { position: relative; flex: 2; }
.location-search-input, .locker-input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 12px; box-sizing: border-box; }
.locker-input { flex: 1; }
.search-dropdown { position: absolute; top: 100%; left: 0; right: 0; background: #fff; border: 1px solid #d1b894; z-index: 10; max-height: 150px; overflow-y: auto; list-style: none; padding: 0; margin: 0; }
.search-dropdown li { padding: 8px; border-bottom: 1px solid #eee; cursor: pointer; }
.lib-name { display: block; font-size: 12px; font-weight: 600; }
.lib-addr { font-size: 10px; color: #999; }
.btn-save-location { width: 100%; padding: 10px; background: #81532e; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.library-card { background: #fdfaf7; border: 1px solid #efeae5; border-radius: 6px; padding: 10px; margin-top: 5px; }
.locker-tag-row { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; background: #fff; padding: 4px 8px; border-radius: 4px; }
.action-buttons { margin-top: 20px; display: flex; flex-direction: column; gap: 10px; }
.request-btn { padding: 12px; border: 1.5px solid #81532e; background: #fff; color: #81532e; border-radius: 6px; font-weight: 600; cursor: pointer; }
.confirm-btn { padding: 12px; background: #81532e; color: #fff; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; }
.status-notice { padding: 12px; background: #fcfcfc; border: 1px dashed #ddd; border-radius: 6px; color: #777; font-size: 12px; text-align: center; }
</style>