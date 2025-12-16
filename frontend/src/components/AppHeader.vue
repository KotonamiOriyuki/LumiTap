<template>
  <header class="app-header">
    <div class="header-left">
      <router-link to="/" class="logo">LumiTap</router-link>
      <nav class="nav-links">
        <router-link to="/" :class="{ active: route.name === 'forum' }">Forum</router-link>
        <router-link to="/songs" :class="{ active: route.name === 'songs' }">Songs</router-link>
        <router-link to="/rankings" :class="{ active: route.name === 'rankings' }">Rankings</router-link>
      </nav>
    </div>
    <div class="header-right">
      <button v-if="userStore.isAuthenticated" class="upload-btn" @click="openUpload">Upload</button>
      <router-link v-if="userStore.isAuthenticated" to="/me" class="user-avatar">
        <img :src="userStore.user?.avatar || defaultAvatar" alt="avatar" />
      </router-link>
      <div v-else class="user-avatar" @click="openLogin">
        <img :src="defaultAvatar" alt="avatar" />
      </div>
    </div>
  </header>
</template>

<script setup>
import { inject } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const userStore = useUserStore()
const openLogin = inject('openLogin')
const openUpload = inject('openUpload')

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23333" width="100" height="100"/><circle fill="%23666" cx="50" cy="35" r="20"/><ellipse fill="%23666" cx="50" cy="85" rx="35" ry="25"/></svg>'
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(90deg, #00d4ff 0%, #0099cc 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #1a1a1a;
  font-style: italic;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: #1a1a1a;
  font-size: 14px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-links a:hover {
  background-color: rgba(0, 0, 0, 0.1);
  text-decoration: none;
}

.nav-links a.active {
  color: #00d4ff;
  background-color: #1a1a1a;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-btn {
  background-color: #1a1a1a;
  color: #00d4ff;
  border: none;
  padding: 6px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s;
}

.upload-btn:hover {
  background-color: #2a2a2a;
}

.user-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid #1a1a1a;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>