<template>
  <div>
    <TheNavbar />

    <router-view />

    <Footer />
  </div>
</template>

<script>
// components 폴더에 만든 TheNavbar를 불러옵니다.
import TheNavbar from './components/TheNavbar.vue'
import Footer from './components/Footer.vue'

export default {
  components: {
    TheNavbar,
    Footer,
  }
}
</script>