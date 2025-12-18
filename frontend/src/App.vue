<!-- Created: Dec 13, 16:50 -->
<!-- Ver 1.2 -->
<!--Changelog: Dec 14 20:30, added upload dialog for beatmaps-->
<!--Changelog: Dec 15 23:30, added isGamePlay to adjust header and footer-->
<template>
  <div id="app">
<!--    Chenxi Liu: Debug, use v-if to hidden header correctly   -->
    <AppHeader v-if="!isGamePlay" />

    <main :class="{ 'with-header': !isGamePlay }">
      <router-view />
    </main>

    <LoginDialog v-model="showLogin" @switch-to-register="switchToRegister" />
    <RegisterDialog v-model="showRegister" @switch-to-login="switchToLogin" />
<!--    Zixiao Shen: Added upload dialog  -->
    <UploadDialog v-model="showUpload" />
    <AppFooter v-if="!isGamePlay" />
  </div>
</template>

<script setup>
import { ref, computed, provide, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from './stores/user'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import LoginDialog from './components/LoginDialog.vue'
import RegisterDialog from './components/RegisterDialog.vue'
import UploadDialog from './components/UploadDialog.vue'

const route = useRoute()
const userStore = useUserStore()

const showLogin = ref(false)
const showRegister = ref(false)
const showUpload = ref(false)

// Chenxi Liu: flag
const isGamePlay = computed(() => route.name === 'gameplay')

const switchToRegister = () => {
  showLogin.value = false
  showRegister.value = true
}

const switchToLogin = () => {
  showRegister.value = false
  showLogin.value = true
}

const openLogin = () => {
  showLogin.value = true
}

const openUpload = () => {
  showUpload.value = true
}

provide('openLogin', openLogin)
provide('openUpload', openUpload)

onMounted(() => {
  userStore.checkAuth()
})

</script>

<style scoped>
#app {
  min-height: 100vh;
}

main {
  min-height: 100vh;
}

main.with-header {
  padding-top: 50px;
}
</style>