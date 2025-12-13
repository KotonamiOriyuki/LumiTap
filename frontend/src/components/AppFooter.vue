<!-- Created: Dec 13 16:30 -->
 <!-- Version 1.0 -->
  <!-- CopyRight Footer -->
<template>
  <footer class="app-footer">
    <div class="footer-container">
      <p>&copy; {{ currentYear }} LumiTap Powered. <a href="https://www.copyright.gov/dmca-directory/" target="_blank" rel="noopener noreferrer" class="dmca-link">DMCA Copyrights</a></p>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  width: 100%;
  background-color: #222222;
  color: #aaaaaa;
  padding: 15px 20px;
  text-align: center;
  font-size: 14px;
  border-top: 1px solid #333333;
  flex-shrink: 0;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>