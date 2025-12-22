<template>
  <div>
    <TheNavbar />

    <router-view />
  </div>
</template>

<script>
// components 폴더에 만든 TheNavbar를 불러옵니다.
import TheNavbar from './components/TheNavbar.vue'

export default {
  components: {
    TheNavbar
  }
}
</script>