<!--Created Dec 16, 21:00-->
<!--Views of a gameplay result-->
<!--Ver 1.0-->
<template>
  <div class="result-view" v-if="beatmap">
    <div class="result-container">
      <div class="beatmap-header" :style="{ backgroundImage: `url(${beatmap.background})` }">
        <div class="header-overlay">
          <div class="header-top">
            <router-link :to="`/profile/${beatmap.uploader_uid}`" class="uploader">
              Uploaded by: {{ beatmap.uploader_name }}
            </router-link>
            <span class="bpm">BPM: {{ beatmap.bpm }}</span>
          </div>
          <div class="header-bottom">
            <h1 class="title">{{ beatmap.title }}</h1>
            <p class="artist">{{ beatmap.artist }}</p>
          </div>
        </div>
      </div>

      <div class="result-actions">
        <div class="diff-badge" :style="diffStyle">
          {{ diffInfo?.name }} {{ diffInfo?.level }}
        </div>
        <div class="action-buttons">
          <button class="back-btn" @click="goBack">Back</button>
          <button class="replay-btn" @click="playAgain">Play Again</button>
        </div>
      </div>

      <h2 class="score-title">Your Score</h2>
      <div class="score-card">
        <div class="rank-display" :style="{ color: rankColor }">{{ result.rank }}</div>
        <div class="score-info">
          <div class="score-value">{{ result.score.toLocaleString() }}</div>
          <div class="accuracy-value">{{ result.accuracy.toFixed(2) }}% Accuracy</div>
        </div>
        <div class="score-details">
          <div class="judgment-counts">
            Great: {{ result.greatCount }}, Good: {{ result.goodCount }}, Miss: {{ result.missCount }}
          </div>
          <div class="ranking-info">
            Ranking: <span class="ranking-number">#{{ ranking }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDifficultyStyle, getRankColor } from '../utils/scoring'
import api from '../utils/api'

const route = useRoute()
const router = useRouter()

const beatmap = ref(null)
const diffInfo = ref(null)
const result = ref({
  score: 0,
  accuracy: 0,
  rank: 'D',
  greatCount: 0,
  goodCount: 0,
  missCount: 0,
  maxCombo: 0
})
const ranking = ref(0)

const diffStyle = computed(() => {
  if (!diffInfo.value) return {}
  const style = getDifficultyStyle(diffInfo.value.level)
  return { backgroundColor: style.bg, color: style.text }
})

const rankColor = computed(() => getRankColor(result.value.rank))

const goBack = () => {
  if (diffInfo.value) {
    router.push(`/beatmap/${diffInfo.value.sid}`)
  } else {
    router.push('/songs')
  }
}

const playAgain = () => {
  router.push(`/play/${route.params.bid}`)
}

onMounted(async () => {
  const savedResult = sessionStorage.getItem('gameResult')
  if (savedResult) {
    result.value = JSON.parse(savedResult)
  }

  try {
    const res = await api.get(`/beatmaps/difficulty/${route.params.bid}`)
    diffInfo.value = res.data
    beatmap.value = res.data.beatmap

    const leaderboardRes = await api.get(`/scores/leaderboard/${route.params.bid}`)
    const userRank = leaderboardRes.data.findIndex(s => s.score <= result.value.score)
    ranking.value = userRank === -1 ? leaderboardRes.data.length + 1 : userRank + 1
  } catch (e) {
    console.error('Failed to load result data')
  }
})
</script>

<style scoped>
.result-view {
  min-height: calc(100vh - 50px);
  padding: 30px;
}

.result-container {
  max-width: 900px;
  margin: 0 auto;
}

.beatmap-header {
  height: 250px;
  background-size: cover;
  background-position: center;
  border-radius: 7px 7px 0 0;
  overflow: hidden;
}

.header-overlay {
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.7) 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.header-top {
  display: flex;
  justify-content: space-between;
}

.uploader {
  color: #ffffff;
  font-size: 14px;
}

.bpm {
  color: #ffffff;
  font-size: 14px;
}

.header-bottom {
  padding-bottom: 10px;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 5px;
}

.artist {
  font-size: 16px;
  color: #cccccc;
}

.result-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background-color: #2a2a2a;
  border-radius: 0 0 7px 7px;
}

.diff-badge {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.back-btn, .replay-btn {
  padding: 10px 25px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.back-btn {
  background-color: #00d4ff;
  color: #1a1a1a;
}

.back-btn:hover {
  background-color: #00b8d9;
}

.replay-btn {
  background-color: #00d4ff;
  color: #1a1a1a;
}

.replay-btn:hover {
  background-color: #00b8d9;
}

.score-title {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  margin: 25px 0 15px 10px;
}

.score-card {
  display: flex;
  align-items: center;
  padding: 25px;
  background-color: #3a3a3a;
  border-radius: 7px;
  gap: 25px;
}

.rank-display {
  font-size: 48px;
  font-weight: bold;
  min-width: 80px;
  text-align: center;
}

.score-info {
  flex: 1;
}

.score-value {
  font-size: 28px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 5px;
}

.accuracy-value {
  font-size: 16px;
  color: #cccccc;
}

.score-details {
  text-align: right;
}

.judgment-counts {
  font-size: 14px;
  color: #aaaaaa;
  margin-bottom: 5px;
}

.ranking-info {
  font-size: 14px;
  color: #aaaaaa;
}

.ranking-number {
  color: #00d4ff;
  font-weight: bold;
}
</style>