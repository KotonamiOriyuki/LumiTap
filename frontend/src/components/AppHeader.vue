```vue
<template>
  <header class="app-header">
    <div class="mobile-menu-toggle" @click="toggleMobileMenu">
      <span></span>
      <span></span>
      <span></span>
    </div>

    <div class="header-left">
      <router-link to="/" class="logo">LumiTap</router-link>
      <nav class="nav-links" :class="{ 'mobile-open': mobileMenuOpen }">
        <router-link to="/" :class="{ active: route.name === 'forum' }" @click="closeMobileMenu">Forum</router-link>
        <router-link to="/songs" :class="{ active: route.name === 'songs' }" @click="closeMobileMenu">Songs</router-link>
        <router-link to="/rankings" :class="{ active: route.name === 'rankings' }" @click="closeMobileMenu">Rankings</router-link>
      </nav>
    </div>

    <div class="header-right">
      <button v-if="userStore.isAuthenticated" class="upload-btn" @click="openUpload">Upload</button>
      <router-link v-if="userStore.isAuthenticated" to="/me" class="user-avatar" @click="closeMobileMenu">
        <img :src="userStore.user?.avatar || defaultAvatar" alt="avatar" />
      </router-link>
      <div v-else class="user-avatar" @click="openLogin">
        <img :src="defaultAvatar" alt="avatar" />
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, inject, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const userStore = useUserStore()
const openLogin = inject('openLogin')
const openUpload = inject('openUpload')

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23333" width="100" height="100"/><circle fill="%23666" cx="50" cy="35" r="20"/><ellipse fill="%23666" cx="50" cy="85" rx="35" ry="25"/></svg>'

const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleResize = () => {
  if (window.innerWidth > 768) {
    closeMobileMenu()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(to bottom, rgba(0, 20, 40, 0.8) 0%, rgba(0, 40, 80, 0.3) 30%, transparent 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  font-style: italic;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
  white-space: nowrap;
}

.nav-links {
  display: flex;
  gap: 15px;
}

.nav-links a {
  color: #ffffff;
  font-size: 14px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s ease;
  text-decoration: none;
}

.nav-links a:hover {
  background-color: rgba(0, 150, 255, 0.15);
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.7);
}

.nav-links a.active {
  color: #00d4ff;
  background-color: rgba(0, 50, 100, 0.5);
  text-shadow: 0 0 12px rgba(0, 212, 255, 1);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-btn {
  background-color: rgba(0, 30, 60, 0.7);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.upload-btn:hover {
  background-color: rgba(0, 212, 255, 0.15);
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 24px;
  height: 18px;
  cursor: pointer;
}

.mobile-menu-toggle span {
  display: block;
  height: 2px;
  width: 100%;
  background-color: #ffffff;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.nav-links a:focus {
  outline: 2px solid #00d4ff;
  outline-offset: 2px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 10px;
    height: 45px;
  }

  .mobile-menu-toggle {
    display: flex;
    margin-right: 10px;
  }

  .nav-links {
    position: fixed;
    top: 45px;
    left: 0;
    right: 0;
    flex-direction: column;
    background: rgba(0, 20, 40, 0.95);
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    padding: 15px;
    gap: 10px;
    transform: translateY(-100%);
    opacity: 0;
    transition: all 0.4s ease;
    pointer-events: none;
    border: 1px solid rgba(20, 40, 60, 0.8);
    border-radius: 0;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  }

  .nav-links.mobile-open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: all;
  }

  .nav-links a {
    padding: 12px 15px;
    font-size: 15px;
    text-align: center;
    border-radius: 6px;
    background: transparent;
  }

  .nav-links a:hover {
    background-color: rgba(0, 0, 0, 0.2);
  }

  .nav-links a.active {
    background-color: rgba(0, 50, 100, 0.4);
  }

  .logo {
    font-size: 16px;
  }

  .upload-btn {
    font-size: 11px;
    padding: 4px 10px;
  }

  .user-avatar {
    width: 28px;
    height: 28px;
  }

  .header-left {
    gap: 10px;
  }

  .header-right {
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .logo {
    font-size: 15px;
  }

  .upload-btn {
    display: none;
  }
}

@media (prefers-color-scheme: dark) {
  .app-header {
    background: linear-gradient(to bottom, rgba(0, 20, 40, 0.85) 0%, rgba(0, 40, 80, 0.4) 50%, transparent 100%);
  }

  .nav-links a.active {
    background-color: rgba(0, 50, 100, 0.7);
  }

  .upload-btn {
    background-color: rgba(0, 30, 60, 0.85);
  }

  @media (max-width: 768px) {
    .nav-links {
      background: rgba(0, 20, 40, 0.98);
      border: 1px solid rgba(30, 50, 70, 0.9);
    }
  }
}
</style>
```