<!--Created: Dec 14, 21:30-->
<!--Ver 1.0-->
<!--Card for displaying difficulties-->
<template>
  <div class="song-card" @click="goToDetail" @mouseenter="hovered = true" @mouseleave="hovered = false" :class="{ hovered }">
    <div class="accent-bar">
      <div class="bar-top"></div>
      <div class="bar-bottom"></div>
    </div>
    <div class="song-bg" :style="{ backgroundImage: `url(${song.background || ''})` }">
      <div class="song-overlay">
        <div class="song-info">
          <h3 class="song-title">{{ song.title }}</h3>
          <p class="song-artist">{{ song.artist }}</p>
        </div>
        <div class="song-right">
          <div class="difficulties">
            <DifficultyBadge
              v-for="diff in song.difficulties"
              :key="diff.bid"
              :name="diff.name"
              :level="diff.level"
            />
          </div>
          <div class="uploader">
            By: <router-link :to="`/profile/${song.uploader_uid}`" @click.stop>{{ song.uploader_name }}</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DifficultyBadge from './DifficultyBadge.vue'

const props = defineProps({
  song: Object
})

const router = useRouter()
const hovered = ref(false)

const goToDetail = () => {
  router.push(`/beatmap/${props.song.sid}`)
}
</script>

<style scoped>
.song-card {
  display: flex;
  border-radius: 7px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.song-card.hovered {
  transform: scale(1.01);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.accent-bar {
  width: 8px;
  display: flex;
  flex-direction: column;
  background-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.bar-top, .bar-bottom {
  flex: 1;
  background-color: #1a1a1a;
}

.bar-top {
  border-bottom-right-radius: 4px;
}

.bar-bottom {
  border-top-right-radius: 4px;
}

.song-bg {
  flex: 1;
  background-size: cover;
  background-position: center;
  min-height: 80px;
}

.song-overlay {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.5) 50%, rgba(0,0,0,0.7) 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
}

.song-info {
  flex: 1;
}

.song-title {
  font-size: 16px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 4px;
}

.song-artist {
  font-size: 13px;
  color: #aaaaaa;
}

.song-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.difficulties {
  display: flex;
  gap: 8px;
}

.uploader {
  font-size: 13px;
  color: #aaaaaa;
  min-width: 120px;
  text-align: right;
}

.uploader a {
  color: #00d4ff;
}
</style>