<!--Created: Dec 17, 18:00-->
<!--Ver 1.0-->
<!--Preview of a beatmap set.-->
<template>
  <div class="beatmap-detail-view" v-if="beatmap">
    <div class="detail-container">
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

      <div class="difficulty-selector">
        <div
          v-for="diff in beatmap.difficulties"
          :key="diff.bid"
          class="diff-item"
          :class="{ selected: selectedDiff?.bid === diff.bid }"
          :style="getDiffStyle(diff.level)"
          @click="selectDifficulty(diff)"
        >
          {{ diff.name }} {{ diff.level }}
        </div>
        <button class="play-btn" @click="startPlay">Play</button>
      </div>

      <h2 class="leaderboard-title">Leaderboard</h2>
      <div class="leaderboard-card">
        <LeaderboardItem
          v-for="(score, index) in leaderboard"
          :key="score.scid"
          :position="score.position"
          :uid="score.uid"
          :username="score.username"
          :score="score.score"
          :accuracy="score.accuracy"
          :rank="score.rank"
          :index="index"
        />
        <div v-if="leaderboard.length === 0" class="no-scores">
          No scores yet
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getDifficultyStyle } from '../utils/scoring'
import api from '../utils/api'
import LeaderboardItem from '../components/LeaderboardItem.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const beatmap = ref(null)
const selectedDiff = ref(null)
const leaderboard = ref([])

const getDiffStyle = (level) => {
  const style = getDifficultyStyle(level)
  return {
    backgroundColor: style.bg,
    color: style.text
  }
}

const selectDifficulty = (diff) => {
  selectedDiff.value = diff
  loadLeaderboard()
}

const loadLeaderboard = async () => {
  if (!selectedDiff.value) return
  try {
    const res = await api.get(`/scores/leaderboard/${selectedDiff.value.bid}`)
    leaderboard.value = res.data
  } catch (e) {
    console.error('Failed to load leaderboard')
  }
}

const startPlay = () => {
  if (!userStore.isAuthenticated) {
    ElMessage.warning('Please login to play')
    return
  }
  if (!selectedDiff.value) {
    ElMessage.warning('Please select a difficulty')
    return
  }
  router.push(`/play/${selectedDiff.value.bid}`)
}

onMounted(async () => {
  try {
    const res = await api.get(`/beatmaps/${route.params.sid}`)
    beatmap.value = res.data
    if (beatmap.value.difficulties.length > 0) {
      selectedDiff.value = beatmap.value.difficulties[0]
      loadLeaderboard()
    }
  } catch (e) {
    console.error('Failed to load beatmap')
  }
})
</script>

<style scoped>
.beatmap-detail-view {
  min-height: calc(100vh - 50px);
  padding: 30px;
}

.detail-container {
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

.difficulty-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  background-color: #2a2a2a;
  border-radius: 0 0 7px 7px;
}

.diff-item {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.diff-item.selected {
  box-shadow: 0 0 0 3px #00d4ff, 0 0 15px rgba(0, 212, 255, 0.5);
}

.play-btn {
  margin-left: auto;
  background-color: #00d4ff;
  color: #1a1a1a;
  border: none;
  padding: 10px 30px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.play-btn:hover {
  background-color: #00b8d9;
}

.leaderboard-title {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  margin: 25px 0 15px 10px;
}

.leaderboard-card {
  background-color: #3a3a3a;
  border-radius: 7px;
  overflow: hidden;
}

.no-scores {
  padding: 30px;
  text-align: center;
  color: #666666;
}
</style>