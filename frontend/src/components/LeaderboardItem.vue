<!--Created: Dec 18, 19:00-->
<!--Ver 1.1-->
<!--Component of leaderboard-->
<!--Changelog: Hidden long description when space is limited-->
<template>
  <div class="leaderboard-item" :class="{ odd: index % 2 === 1 }" @click="goToProfile">
    <div class="rank-bar" :style="rankBarStyle">
      <span class="rank-number">#{{ position }}</span>
    </div>
    <div class="item-content">
      <div class="rank-badge" :style="{ color: rankColor }">{{ rank }}</div>
      <div class="player-name">{{ username }}</div>
      <div class="score-info">
<!--    Yiwen Wang: Hidden several contents in mobile client    -->
        <span class="desktop-text">Score: {{ score.toLocaleString() }}, Accuracy: {{ accuracy.toFixed(2) }}%</span>
        <span class="mobile-text">{{ score.toLocaleString() }}, Acc {{ accuracy.toFixed(2) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getRankColor } from '../utils/scoring'

const props = defineProps({
  position: Number,
  uid: String,
  username: String,
  score: Number,
  accuracy: Number,
  rank: String,
  index: Number
})

const router = useRouter()

const rankColor = computed(() => getRankColor(props.rank))

const rankBarStyle = computed(() => {
  if (props.position === 1) return { backgroundColor: '#ffb300' }
  if (props.position === 2) return { backgroundColor: '#b0bec5' }
  if (props.position === 3) return { backgroundColor: '#cd7f32' }
  return { backgroundColor: '#4a4a4a' }
})

const goToProfile = () => {
  router.push(`/profile/${props.uid}`)
}
</script>

<style scoped>
.leaderboard-item {
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: background-color 0.2s;
}

.leaderboard-item:hover {
  background-color: #3a3a3a;
}

.leaderboard-item.odd .item-content {
  background-color: #2a2a2a;
}

.rank-bar {
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}

.rank-number {
  font-size: 12px;
  font-weight: bold;
  color: #1a1a1a;
}

.item-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 8px 15px;
  background-color: #333333;
  gap: 15px;
  min-width: 0;
}

.rank-badge {
  font-size: 16px;
  font-weight: bold;
  min-width: 30px;
}

.player-name {
  flex: 1;
  font-size: 14px;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.score-info {
  font-size: 13px;
  color: #aaaaaa;
}

.mobile-text {
  display: none;
}

@media (max-width: 768px) {
  .desktop-text {
    display: none;
  }
  .mobile-text {
    display: inline;
  }
  .item-content {
    gap: 10px;
    padding: 8px 10px;
  }
}
</style>