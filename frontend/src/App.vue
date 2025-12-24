<template>
  <div :class="['app-wrapper', { 'is-home': route.path === '/' }]">
    <TheNavbar />

    <main class="app-main">
      <router-view />
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import TheNavbar from './components/TheNavbar.vue'
import Footer from './components/Footer.vue'

const route = useRoute()
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #fdfaf5; 
}

#app {
  height: 100%;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png');
  background-attachment: fixed;
}

.app-wrapper.is-home {
  background-image: none !important;
  background-color: #fdfaf5; 
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>