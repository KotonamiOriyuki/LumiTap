<!-- Created: Dec 13 16:30 -->
 <!-- Version 1.0 -->
  <!-- CopyRight Header -->
<template>
  <header class="app-header">
    <div class="header-left">
      <router-link to="/" class="logo">LumiTap</router-link>
      <nav class="nav-links">
        <router-link to="/">Forum</router-link>
        <router-link to="/songs">Songs</router-link>
        <router-link to="/rankings">Rankings</router-link>
      </nav>
    </div>
    <div class="header-right">
      <!-- Placeholder, this will be filled after the register function is completed -->
    </div>
  </header>
</template>

<script setup>

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

</style>