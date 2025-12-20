<!--Created: Dec 18, 15:30-->
<!--Ver 1.0-->
<!--Display the global ranking-->
<template>
  <div class="rankings-view">
    <div class="rankings-container">
      <h1 class="rankings-title">Global Rankings</h1>
      <div class="rankings-card">
        <div
          v-for="(user, index) in rankings"
          :key="user.uid"
          class="ranking-item"
          :class="{ odd: index % 2 === 1 }"
          @click="goToProfile(user.uid)"
        >
          <div class="rank-bar" :style="getRankBarStyle(user.rank)">
            <span class="rank-number">#{{ user.rank }}</span>
          </div>
          <div class="item-content">
            <div class="user-avatar">
              <img :src="user.avatar || defaultAvatar" alt="avatar" />
            </div>
            <div class="user-name">{{ user.username }}</div>
            <div class="user-ep consolas" :style="{ color: getEPColorValue(user.ep) }" :class="{ 'high-ep': isHighEPValue(user.ep) }">
              EP: {{ user.ep.toFixed(2) }}
            </div>
          </div>
        </div>
        <div v-if="rankings.length === 0" class="no-rankings">
          No rankings yet
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getEPColor, isHighEP } from '../utils/scoring'
import api from '../utils/api'

const router = useRouter()
const rankings = ref([])

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23333" width="100" height="100"/><circle fill="%23666" cx="50" cy="35" r="20"/><ellipse fill="%23666" cx="50" cy="85" rx="35" ry="25"/></svg>'

const getRankBarStyle = (rank) => {
  if (rank === 1) return { backgroundColor: '#ffb300' }
  if (rank === 2) return { backgroundColor: '#b0bec5' }
  if (rank === 3) return { backgroundColor: '#cd7f32' }
  return { backgroundColor: '#4a4a4a' }
}

const getEPColorValue = (ep) => {
  return getEPColor(ep)
}

const isHighEPValue = (ep) => {
  return isHighEP(ep)
}

const goToProfile = (uid) => {
  router.push(`/profile/${uid}`)
}

onMounted(async () => {
  try {
    const res = await api.get('/users/rankings/all')
    rankings.value = res.data
  } catch (e) {
    console.error('Failed to load rankings')
  }
})
</script>

<style scoped>
.rankings-view {
  min-height: calc(100vh - 50px);
  padding: 30px;
}

.rankings-container {
  max-width: 900px;
  margin: 0 auto;
}

.rankings-title {
  font-size: 28px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 20px;
}

.rankings-card {
  background-color: #3a3a3a;
  border-radius: 7px;
  overflow: hidden;
}

.ranking-item {
  display: flex;
  cursor: pointer;
  transition: background-color 0.2s;
}

.ranking-item:hover {
  background-color: #4a4a4a;
}

.ranking-item.odd .item-content {
  background-color: #2a2a2a;
}

.ranking-item.odd:hover .item-content {
  background-color: #3a3a3a;
}

.rank-bar {
  width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 0;
}

.rank-number {
  font-size: 14px;
  font-weight: bold;
  color: #1a1a1a;
}

.item-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: #333333;
  gap: 15px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  flex: 1;
  font-size: 16px;
  font-weight: bold;
  color: #ffffff;
}

.user-ep {
  font-size: 16px;
  font-weight: bold;
}

.user-ep.high-ep {
  text-shadow: 0 0 10px currentColor, 0 0 20px currentColor;
}

.no-rankings {
  padding: 30px;
  text-align: center;
  color: #666666;
}
</style>