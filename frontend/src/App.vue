<!-- Created: Dec 13, 16:50 -->
 <!-- Ver 1.0 -->
<template>
  <div id="app">
    <AppHeader/>

    <main :class="'with-header'">
      <router-view />
    </main>
    <AppFooter/>

  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'

const route = useRoute()

</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex-grow: 1;
}

main.with-header {
  padding-top: 50px;
}
</style>