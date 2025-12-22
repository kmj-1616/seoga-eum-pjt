<template>
  <div class="login-container">
    <h1>로그인 페이지</h1>
    <p>화면이 보인다면 성공입니다!</p>
    <div class="login-box">
      <input type="text" placeholder="이메일">
      <input type="password" placeholder="비밀번호">
      <button>로그인</button>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  padding: 100px;
  text-align: center;
}
.login-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 300px;
  margin: 20px auto;
}
</style>