<!--Created: Dec 18, 21:00-->
<!--Ver 1.0-->
<!--Component that display the personal best record sorted by EP-->
<template>
  <div class="score-card" :class="{ odd: index % 2 === 1 }" @click="goToBeatmap">
    <div class="rank-badge" :style="{ color: rankColor }">{{ score.rank }}</div>
    <div class="song-name">{{ score.title }} [{{ score.difficulty_name }}]</div>
    <div class="score-details">
      <span>Score: {{ score.score.toLocaleString() }}, Accuracy: {{ score.accuracy.toFixed(2) }}%</span>
      <span class="potential">Potential: {{ score.potential.toFixed(2) }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getRankColor } from '../utils/scoring'

const props = defineProps({
  score: Object,
  index: Number
})

const router = useRouter()

const rankColor = computed(() => getRankColor(props.score.rank))

const goToBeatmap = () => {
  if (props.score.sid) {
    router.push(`/beatmap/${props.score.sid}`)
  }
}
</script>

<style scoped>
.score-card {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background-color: #333333;
  gap: 15px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.score-card:hover {
  background-color: #3a3a3a;
}

.score-card.odd {
  background-color: #2a2a2a;
}

.score-card.odd:hover {
  background-color: #333333;
}

.rank-badge {
  font-size: 18px;
  font-weight: bold;
  min-width: 35px;
}

.song-name {
  flex: 1;
  font-size: 14px;
  color: #ffffff;
}

.score-details {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #aaaaaa;
}

.potential {
  color: #00d4ff;
}
</style>