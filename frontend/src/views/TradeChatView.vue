<template>
  <div class="chat-outer-container">
    <div class="chat-container">
      <header class="chat-header">
        <button class="back-btn" @click="$router.back()">
          <span class="arrow">←</span> 이전으로 돌아가기
        </button>
        <div class="book-context">
          <h2 class="community-title">서책 거래 소통창</h2>
          <p class="community-subtitle">「{{ bookInfo.title }}」 도서를 위한 안전하고 따뜻한 공간</p>
        </div>
      </header>

      <div class="chat-main-layout">
        <section class="chat-window">
          <div class="message-list" ref="messageBox">
            <div v-if="!messages || messages.length === 0" class="no-messages">
              판매자/구매자와 따뜻한 인사를 나누며 대화를 시작해보세요.
            </div>
            
            <div v-for="(msg, index) in messages" :key="msg?.id || index">
              <div v-if="shouldShowDivider(index)" class="date-divider">
                <span class="date-text">{{ formatDateDivider(messages[index].created_at) }}</span>
              </div>

              <div :class="['message-wrapper', { 'my-message': isMyMessage(msg) }]">
                <div v-if="!isMyMessage(msg)" class="user-avatar">
                  {{ msg?.nickname ? msg.nickname[0] : '익' }}
                </div>
                
                <div class="message-content-group">
                  <div v-if="!isMyMessage(msg)" class="user-nickname">
                    {{ msg?.nickname || '상대방' }}
                  </div>
                  <div class="message-bubble-row">
                    <div class="message-bubble">{{ msg?.content }}</div>
                    <span class="message-time">{{ formatKoreanTime(msg?.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="message-input-area">
            <textarea 
              v-model="newMessage" 
              placeholder="메시지를 입력하세요..." 
              @keydown.enter.prevent="handleEnter"
            ></textarea>
            <button 
              class="send-btn" 
              @click="sendMessage" 
              :disabled="!newMessage || !newMessage.trim()"
            >전송</button>
          </div>
        </section>

        <aside class="chat-sidebar">
          <h3 class="sidebar-title">거래 도서 정보</h3>
          <TransactionInfo 
            v-if="bookInfo.title"
            :book-title="bookInfo.title"
            :book-author="bookInfo.author"
            :book-price="tradeData.price"
            :book-grade="tradeData.grade"
            :status="tradeData.status"
            :library-name="tradeData.library_name"
            :library-address="tradeData.library_address"
            :locker-number="tradeData.locker_number"
            @confirm-receipt="handleConfirmReceipt"
          />
          
          <div class="sidebar-footer-notice">
            <p>💡 상대방이 도서관 보관함에 책을 넣으면 '수령 완료' 버튼이 활성화됩니다. 수령 후 버튼을 눌러주세요.</p>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import TransactionInfo from '@/components/TransactionInfo.vue';

const route = useRoute();
const tradeId = route.params.trade_id; // URL의 :trade_id 파라미터

// 상태 관리 변수
const messages = ref([]);
const newMessage = ref('');
const messageBox = ref(null);
const currentUserId = ref(localStorage.getItem('user_id'));

// 도서 및 거래 정보 (나중에 API로 로드)
const bookInfo = ref({ title: '', author: '' });
const tradeData = ref({
  price: 0,
  grade: '상급',
  status: 'REQUESTED', // 기본 상태
  library_name: '강남도서관',
  library_address: '서울시 강남구 개포로 235',
  locker_number: 'A-12'
});

// --- 유틸리티 함수 ---
const isMyMessage = (msg) => String(msg.user_id) === String(currentUserId.value);

const shouldShowDivider = (index) => {
  if (index === 0) return true;
  const current = messages.value[index].created_at?.substring(0, 10);
  const prev = messages.value[index - 1].created_at?.substring(0, 10);
  return current !== prev;
};

const formatDateDivider = (timestamp) => {
  if (!timestamp) return '';
  const [y, m, d] = timestamp.substring(0, 10).split('-');
  return `${y}년 ${parseInt(m)}월 ${parseInt(d)}일`;
};

const formatKoreanTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  let hours = date.getHours();
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? '오후' : '오전';
  hours = hours % 12 || 12;
  return `${ampm} ${hours}:${minutes}`;
};

// --- API 호출 함수 ---
const fetchTradeDetails = async () => {
  try {
    // 1. 동료가 만든 백엔드 상세 API 주소로 교체 예정
    // const res = await axios.get(`http://127.0.0.1:8000/api/v1/trades/${tradeId}/`);
    
    // 2. 받아온 데이터로 화면 갱신
    // bookInfo.value = { title: res.data.book_title, author: res.data.book_author };
    // tradeData.value = { 
    //    price: res.data.price, 
    //    status: res.data.status, // 'REQUESTED', 'LIBRARY_STORED' 등
    //    ... 
    // };
    
    // 현재는 화면 확인용 더미
    bookInfo.value = { title: '데미안', author: '헤르만 헤세' };
    tradeData.value.status = 'LIBRARY_STORED'; 
  } catch (err) {
    console.error("거래 정보 로드 실패", err);
  }
};

const fetchMessages = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/v1/trade/${tradeId}/messages/`);
    messages.value = res.data;
    await nextTick();
    scrollToBottom();
  } catch (err) {
    console.error("메시지 로드 실패", err);
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim()) return;
  const token = localStorage.getItem('access_token');
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/v1/trade/${tradeId}/messages/`,
      { content: newMessage.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    newMessage.value = '';
    fetchMessages();
  } catch (err) {
    alert("전송 실패");
  }
};

const handleConfirmReceipt = async () => {
  if (!confirm("도서를 안전하게 수령하셨습니까? 거래가 완료 처리됩니다.")) return;
  try {
    // await axios.patch(`URL/trades/${tradeId}/`, { status: 'COMPLETED' });
    tradeData.value.status = 'COMPLETED';
    alert("거래가 완료되었습니다. 인연을 맺어주셔서 감사합니다.");
  } catch (err) {
    alert("처리 중 오류가 발생했습니다.");
  }
};

const handleEnter = (e) => { if (!e.shiftKey) sendMessage(); };
const scrollToBottom = () => { if (messageBox.value) messageBox.value.scrollTop = messageBox.value.scrollHeight; };

// --- 생명 주기 ---
let pollInterval;
onMounted(() => {
  fetchTradeDetails();
  fetchMessages();
  pollInterval = setInterval(fetchMessages, 3000);
});
onUnmounted(() => clearInterval(pollInterval));
</script>

<style scoped>
/* 폰트 및 기본 설정 */
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500;700&display=swap');

.chat-outer-container { 
  min-height: calc(100vh - 85px); 
  font-family: 'Hahmlet', serif; 
  padding: 20px 0; 
}

.chat-container { 
  max-width: 1200px; 
  margin: 0 auto; 
  display: flex; 
  flex-direction: column; 
  height: 85vh; 
  padding: 0 20px; 
}

/* 헤더 & 이전으로 버튼 스타일 (수정됨) */
.chat-header { margin-bottom: 20px; }
.back-btn { 
  background: none; 
  border: none; 
  color: #81532e; 
  cursor: pointer; 
  font-size: 16px; 
  margin-bottom: 12px; 
  font-family: 'Hahmlet', serif;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 0;
  transition: 0.2s;
}
.back-btn:hover { color: #4a3423; transform: translateX(-3px); }
.community-title { font-size: 26px; font-weight: 700; color: #4a3423; margin: 0; }
.community-subtitle { font-size: 18px; color: #81532e; margin: 5px 0 0 0; }

.chat-main-layout { display: flex; gap: 20px; flex: 1; overflow: hidden; }

/* 채팅창 스타일 */
.chat-window { 
  flex: 2.5; 
  background: white; 
  border: 1px solid #d1b894; 
  display: flex; 
  flex-direction: column; 
  box-shadow: 10px 10px 20px rgba(0,0,0,0.03);
}

.message-list { 
  flex: 1; 
  padding: 30px; 
  overflow-y: auto; 
  display: flex; 
  flex-direction: column; 
  gap: 24px; 
}

/* 메시지 버블 스타일 통일 */
.message-wrapper { display: flex; gap: 12px; width: 100%; max-width: 85%; }
.my-message { align-self: flex-end; flex-direction: row-reverse; margin-left: auto; }
.user-avatar { 
  width: 40px; height: 40px; background: #f5ece0; border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; 
  color: #81532e; font-weight: 700; border: 1px solid #d1b894; flex-shrink: 0; 
}
.message-content-group { display: flex; flex-direction: column; }
.my-message .message-content-group { align-items: flex-end; }
.user-nickname { font-size: 13px; color: #6d5d50; margin-bottom: 6px; font-weight: 500; }
.message-bubble-row { display: flex; align-items: flex-end; gap: 8px; }
.my-message .message-bubble-row { flex-direction: row-reverse; }
.message-bubble { 
  background: #fdfcfb; border: 1px solid #f5ece0; 
  padding: 12px 18px; border-radius: 4px; /* 각진 사각형 스타일 */
  color: #4a3423; line-height: 1.6; font-size: 15px; 
}
.my-message .message-bubble { background: #81532e; color: #fdfaf5; border: none; }
.message-time { font-size: 11px; color: #c4b5a6; flex-shrink: 0; }

.message-input-area { 
  padding: 20px; 
  border-top: 1px solid #f5ece0; 
  display: flex; 
  gap: 12px; 
  background: #fdfcfb; 
  align-items: stretch; 
}
textarea { 
  flex: 1; 
  height: 70px; 
  border: 1px solid #d1b894; 
  padding: 12px; 
  resize: none; 
  font-family: 'Hahmlet', serif; 
  font-size: 15px; 
  outline: none; 
  box-sizing: border-box; 
  margin: 0; 
  background: white;
}
.send-btn { 
  background: #81532e; 
  color: white; 
  border: none; 
  padding: 0 30px; 
  cursor: pointer; 
  border-radius: 2px; 
  font-family: 'Hahmlet', serif; 
  font-weight: 600; 
  font-size: 16px;
  height: 70px; 
  box-sizing: border-box; 
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0; 
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #4a3423;
}

.send-btn:disabled { 
  background: #c4b5a6; 
  cursor: not-allowed; 
}

.chat-sidebar { 
  flex: 1.2; background: white; border: 1px solid #d1b894; 
  padding: 25px; display: flex; flex-direction: column; overflow-y: auto; 
}
.sidebar-title { 
  font-size: 18px; color: #4a3423; margin-bottom: 20px; 
  border-bottom: 2px solid #f5ece0; padding-bottom: 12px; font-weight: 700;
}
.sidebar-footer-notice { 
  margin-top: auto; padding: 15px; background: #fdfaf5; 
  border: 1px dashed #d1b894; font-size: 12px; color: #81532e; line-height: 1.5; 
}

/* 날짜 구분선 스타일 */
.date-divider { display: flex; align-items: center; justify-content: center; margin: 30px 0 20px; position: relative; }
.date-divider::before { content: ""; position: absolute; top: 50%; left: 0; right: 0; height: 1px; background-color: #f5ece0; z-index: 1; }
.date-text { background-color: #fff; padding: 0 15px; font-size: 12px; color: #c4b5a6; z-index: 2; font-weight: 500; }

.no-messages { text-align: center; color: #c4b5a6; margin-top: 50px; font-size: 14px; }
</style>