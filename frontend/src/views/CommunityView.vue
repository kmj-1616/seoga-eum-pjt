<template>
  <div class="chat-outer-container">
    <div class="chat-container">
      <header class="chat-header">
        <button class="back-btn" @click="$router.back()">
          <span class="arrow">←</span> 이전으로 돌아가기
        </button>
        <div class="book-context">
          <h2 class="community-title">{{ bookTitle || '도서 정보를 불러오는 중...' }}</h2>
          <p class="community-subtitle" v-if="bookAuthor">「{{ bookAuthor }}」 작가님의 문장을 함께 나누는 공간</p>
        </div>
      </header>

      <div class="chat-main-layout">
        <section class="chat-window">
          <div class="message-list" ref="messageBox">
            <div v-if="!messages || messages.length === 0" class="no-messages">
              첫 번째 문장을 남겨 커뮤니티를 시작해보세요.
            </div>
            
            <div v-for="(msg, index) in messages" :key="msg?.id || index">
              
            <div 
              v-if="shouldShowDivider(index)" 
              class="date-divider"
            >
              <span class="date-text">{{ formatDateDivider(messages[index].created_at) }}</span>
            </div>
              <div :class="['message-wrapper', { 'my-message': isMyMessage(msg) }]">
                <div v-if="!isMyMessage(msg)" class="user-avatar">
                  {{ msg?.nickname ? msg.nickname[0] : '익' }}
                </div>
                
                <div class="message-content-group">
                  <div v-if="!isMyMessage(msg)" class="user-nickname">
                    {{ msg?.nickname || '익명' }}
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
            <template v-if="currentUserId">
              <textarea 
                v-model="newMessage" 
                placeholder="따뜻한 한마디를 나누어보세요..." 
                @keydown.enter.prevent="handleEnter"
              ></textarea>
              <button 
                class="send-btn" 
                @click="sendMessage" 
                :disabled="!newMessage || !newMessage.trim()"
              >전송</button>
            </template>
            <template v-else>
              <div class="login-required-msg">
                대화에 참여하려면 <router-link :to="`/login?redirect=${$route.fullPath}`">신분 확인</router-link>이 필요합니다.
              </div>
              <button class="send-btn" disabled>전송</button>
            </template>
          </div>
        </section>

        <aside class="chat-sidebar">
          <h3 class="sidebar-title">함께 읽는 이들</h3>
          <ul class="participant-list">
            <li v-if="currentUserId" class="participant-item my-account">
              <span class="status-dot online"></span>
              <span class="p-name"><strong>{{ myNickname || '나' }} (접속 중)</strong></span>
            </li>

            <li v-for="user in activeParticipants" :key="user.id" class="participant-item">
              <span class="status-dot"></span> <span class="p-name">{{ user.name }}</span>
              <span class="status-text">오프라인</span>
            </li>
            
            <li v-if="!currentUserId && activeParticipants.length === 0" class="participant-item">
              <span class="p-name">참여자가 없습니다.</span>
            </li>
          </ul>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const isbn = route.params.isbn;

const messages = ref([]);
const newMessage = ref('');
const bookTitle = ref('');
const bookAuthor = ref('');
const messageBox = ref(null);

// currentUserId와 별개로 목록에 표시할 마지막 닉네임 저장
const currentUserId = ref(localStorage.getItem('user_id'));
const myNickname = ref('');
const lastUserNickname = ref(localStorage.getItem('user_nickname') || '채채'); 

const isMyMessage = (msg) => {
  if (!msg || !msg.user_id || !currentUserId.value) return false;
  return String(msg.user_id) === String(currentUserId.value);
};

// // 1. "2025-12-23 07:08:21..." -> "2025년 12월 23일" (구분선용)
// const formatDateDivider = (timestamp) => {
//   if (!timestamp) return '';
//   const date = new Date(timestamp);
//   return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
// };

// // 2. "2025-12-23 07:08:21..." -> "오전 07:08" (메시지 시간용)
// const formatKoreanTime = (timestamp) => {
//   if (!timestamp) return '';
//   const date = new Date(timestamp);
//   let hours = date.getHours();
//   const minutes = date.getMinutes().toString().padStart(2, '0');
//   const ampm = hours >= 12 ? '오후' : '오전';
  
//   hours = hours % 12;
//   hours = hours ? hours : 12; // 0시는 12시로 표시
  
//   return `${ampm} ${hours.toString().padStart(2, '0')}:${minutes}`;
// };

// 1. 날짜 구분선 여부 결정
const shouldShowDivider = (index) => {
  if (index === 0) return true;
  
  const currentFullDate = getOnlyDate(messages.value[index].created_at);
  const prevFullDate = getOnlyDate(messages.value[index - 1].created_at);
  
  return currentFullDate !== prevFullDate;
};

// 2. 날짜만 추출 (YYYY-MM-DD)
const getOnlyDate = (timestamp) => {
  if (!timestamp) return '';
  // ISO 형식 "2025-12-23T16:08:21..."에서 앞의 10자리만 자름
  return timestamp.substring(0, 10);
};

// 3. 날짜 구분선 텍스트 ("2025년 12월 23일")
const formatDateDivider = (timestamp) => {
  const dateStr = getOnlyDate(timestamp);
  if (!dateStr) return '';
  
  const [year, month, day] = dateStr.split('-');
  return `${year}년 ${parseInt(month)}월 ${parseInt(day)}일`;
};

// 4. 메시지 시간 ("오전 07:08")
const formatKoreanTime = (timestamp) => {
  if (!timestamp) return '';
  
  try {
    const date = new Date(timestamp);
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? '오후' : '오전';
    
    hours = hours % 12 || 12;
    return `${ampm} ${hours.toString().padStart(2, '0')}:${minutes}`;
  } catch (e) {
    return '';
  }
};

const fetchMyProfile = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    currentUserId.value = null; // 로그아웃 상태 명시
    return;
  }
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/users/profile/', {
      headers: { Authorization: `Bearer ${token}` }
    });
    myNickname.value = response.data.nickname;
    lastUserNickname.value = response.data.nickname;
    // 나중에 로그아웃해도 이름을 기억하기 위해 저장
    localStorage.setItem('user_nickname', response.data.nickname);
  } catch (error) {
    console.error("프로필 로드 실패");
  }
};

const fetchBookInfo = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/books/${isbn}/`);
    bookTitle.value = response.data.title;
    bookAuthor.value = response.data.author;
  } catch (error) {
    console.error("도서 정보 로드 실패");
  }
};

const fetchMessages = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/community/${isbn}/messages/`);
    messages.value = response.data.results || [];
    await nextTick();
    scrollToBottom();
  } catch (error) {
    console.error("메시지 로드 실패");
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentUserId.value) return;
  const token = localStorage.getItem('access_token');
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/v1/community/${isbn}/messages/`, 
      { content: newMessage.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    newMessage.value = '';
    setTimeout(() => { fetchMessages(); }, 100);
  } catch (error) {
    alert("메시지 전송에 실패했습니다.");
  }
};

const handleEnter = (e) => { if (!e.shiftKey) sendMessage(); };
const scrollToBottom = () => { if (messageBox.value) messageBox.value.scrollTop = messageBox.value.scrollHeight; };

let pollInterval;
onMounted(() => {
  fetchMyProfile();
  fetchBookInfo();
  fetchMessages();
  pollInterval = setInterval(fetchMessages, 3000);
});

onUnmounted(() => { if (pollInterval) clearInterval(pollInterval); });

// 메시지 내역에서 유저 목록을 추출하는 계산된 속성
const activeParticipants = computed(() => {
  if (!messages.value || messages.value.length === 0) return [];

  // 메시지에서 중복되지 않는 유저 정보(ID, 닉네임) 추출
  const userMap = new Map();
  
  messages.value.forEach(msg => {
    if (msg.user_id && msg.nickname) {
      // 내 아이디가 아닐 때만 목록에 추가 
      if (String(msg.user_id) !== String(currentUserId.value)) {
        userMap.set(msg.user_id, {
          id: msg.user_id,
          name: msg.nickname,
          online: false // 실제 실시간 상태는 알 수 없으므로 기본 오프라인
        });
      }
    }
  });

  return Array.from(userMap.values());
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500;700&display=swap');
.my-account { background: #fdfaf5 !important; border: 1px solid #d1b894 !important; }
.status-dot { width: 9px; height: 9px; border-radius: 50%; background: #e5e7eb; }
.status-dot.online { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
.my-account { background: #fdfaf5; padding: 8px; border-radius: 4px; border: 1px solid #f5ece0; margin-bottom: 10px; }
.my-account .p-name { color: #81532e; }
.no-messages { text-align: center; color: #c4b5a6; margin-top: 50px; font-size: 14px; }
.chat-outer-container { min-height: calc(100vh - 85px); font-family: 'Hahmlet', serif; padding: 20px 0; }
.chat-container { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; height: 85vh; padding: 0 20px; }
.chat-header { margin-bottom: 20px; }
.back-btn { background: none; border: none; color: #81532e; cursor: pointer; font-size: 16px; margin-bottom: 10px; }
.community-title { font-size: 26px; font-weight: 700; color: #4a3423; margin: 0; }
.community-subtitle { font-size: 18px; color: #81532e; margin: 5px 0 0 0; }
.chat-main-layout { display: flex; gap: 20px; flex: 1; overflow: hidden; }
.chat-window { flex: 3; background: white; border: 1px solid #d1b894; display: flex; flex-direction: column; box-shadow: 10px 10px 20px rgba(0,0,0,0.03); }
.message-list {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  display: flex;
  flex-direction: column; 
  gap: 24px;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  width: 100%; 
}

.my-message {
  justify-content: flex-start; 
  flex-direction: row-reverse; 
  margin-left: auto; 
  max-width: 85%; 
}

.message-wrapper:not(.my-message) {
  max-width: 85%;
  align-self: flex-start;
}

.my-message .message-content-group {
  align-items: flex-end; 
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
}

.login-required-msg {
  flex: 1;
  height: 70px; 
  background: #f8f9fa; 
  border: 1px dashed #d1b894;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #81532e;
  font-size: 15px;
  box-sizing: border-box;
}

.login-required-msg a {
  color: #81532e;
  font-weight: 700;
  margin: 0 5px;
  text-decoration: underline;
}

.send-btn {
  background: #81532e;
  color: white;
  border: none;
  padding: 0 30px;
  cursor: pointer;
  border-radius: 2px;
  font-family: 'Hahmlet';
  font-size: 16px;
  font-weight: 600;
  height: 70px; 
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}
.user-avatar { width: 40px; height: 40px; background: #f5ece0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #81532e; font-weight: 700; border: 1px solid #d1b894; flex-shrink: 0; }
.message-content-group { display: flex; flex-direction: column; }
.user-nickname { font-size: 13px; color: #6d5d50; margin-bottom: 6px; font-weight: 500; }
.message-bubble-row { display: flex; align-items: flex-end; gap: 8px; }
.my-message .message-bubble-row { flex-direction: row-reverse; }
.message-bubble { background: #fdfcfb; border: 1px solid #f5ece0; padding: 12px 18px; border-radius: 4px; color: #4a3423; line-height: 1.6; font-size: 15px; }
.my-message .message-bubble { background: #81532e; color: #fdfaf5; border: none; }
.message-time { font-size: 11px; color: #c4b5a6; flex-shrink: 0; }
.message-input-area { 
  padding: 20px; 
  border-top: 1px solid #f5ece0; 
  display: flex; 
  gap: 15px; 
  background: #fdfcfb; 
  align-items: flex-start; 
}
.send-btn:disabled { background: #c4b5a6; cursor: not-allowed; }
.chat-sidebar { flex: 1; background: white; border: 1px solid #d1b894; padding: 25px; display: flex; flex-direction: column; }
.sidebar-title { font-size: 18px; color: #4a3423; margin-bottom: 25px; border-bottom: 2px solid #f5ece0; padding-bottom: 12px; }
.participant-item { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.status-dot { width: 9px; height: 9px; border-radius: 50%; background: #e5e7eb; }
.status-dot.online { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
.p-name { font-size: 15px; color: #4a3423; }
.status-text { font-size: 11px; color: #2ecc71; margin-left: auto; }
.community-notice { background: #fdfaf5; padding: 15px; border: 1px dashed #d1b894; font-size: 12px; color: #81532e; }

.date-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 30px 0 20px;
  position: relative;
}

.date-divider::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #f5ece0; 
  z-index: 1;
}

.date-text {
  background-color: #fdfaf5; 
  padding: 0 15px;
  font-size: 12px;
  color: #c4b5a6;
  z-index: 2;
  font-weight: 500;
  letter-spacing: -0.5px;
}
</style>