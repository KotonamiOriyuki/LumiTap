<!--Created: Dec 18, 21:00-->
<!--Ver 1.1-->
<!--Component that display the personal best record sorted by EP-->
<!--Changelog: Hidden contents when mobile, Dec 30, 18:30-->
<template>
  <div class="score-card" :class="{ odd: index % 2 === 1 }" @click="goToBeatmap">
    <div class="rank-badge" :style="{ color: rankColor }">{{ score.rank }}</div>
    <div class="card-body">
      <div class="song-name">{{ score.title }} [{{ score.difficulty_name }}]</div>
      <div class="score-details">
        <span class="score-val">
          <span class="desktop-text">Score: {{ score.score.toLocaleString() }}, Accuracy: {{ score.accuracy.toFixed(2) }}%</span>
          <span class="mobile-text">{{ score.score.toLocaleString() }}, Acc {{ score.accuracy.toFixed(2) }}%</span>
        </span>
        <span class="potential">
          <span class="desktop-text">Potential: </span>{{ score.potential.toFixed(2) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getRankColor } from '../utils/scoring'
import api from '../utils/api'

const props = defineProps({
  score: Object,
  index: Number
})

const router = useRouter()

const rankColor = computed(() => getRankColor(props.score.rank))

const goToBeatmap = async () => {
  if (props.score.sid) {
    router.push(`/beatmap/${props.score.sid}`)
    return
  }

  if (props.score.bid) {
    try {
      const res = await api.get(`/beatmaps/sid-from-bid/${props.score.bid}`)
      if (res.data && res.data.sid) {
        router.push(`/beatmap/${res.data.sid}`)
      }
    } catch (e) {
      console.error('Failed to fetch sid from bid')
    }
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

.rank-badge {
  font-size: 18px;
  font-weight: bold;
  min-width: 35px;
  text-align: center;
}

.card-body {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 0;
}

.song-name {
  flex: 1;
  font-size: 14px;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.mobile-text {
  display: none;
}

@media (max-width: 768px) {
  .card-body {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  .score-details {
    gap: 10px;
  }
  .desktop-text {
    display: none;
  }
  .mobile-text {
    display: inline;
  }
}
</style>