<!--Created: Dec 14, 21:30-->
<!--Ver 1.1-->
<!--Card for displaying difficulties-->
<!--Changelog: Dec 20, 19:00 Modified the style and fix the bug of neon light effects-->
<template>
  <div class="song-card" @click="goToDetail" @mouseenter="hovered = true" @mouseleave="hovered = false" :class="{ hovered }">
    <div class="song-inner" :style="{ backgroundImage: `url(${song.background || ''})` }">
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
  width: 100%;
  height: 90px;
  background: linear-gradient(90deg, #00d4ff 0%, #1A1A1A 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.song-card.hovered {
  transform: translateY(-2px);
  box-shadow: 3px 3px 5px rgba(0, 212, 255, 0.3);
}

.song-card.hovered .song-inner {
  width: 99.5%;
}

.song-inner {
  width: 99%;
  height: 100%;
  border-top-left-radius: 10px;
  border-bottom-left-radius: 10px;
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
  background-size: cover;
  background-position: center;
  overflow: hidden;
  transition: width 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.3);
  position: relative;
}

.song-overlay {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(26,26,26,0.95) 0%, rgba(26,26,26,0.7) 50%, rgba(26,26,26,0.9) 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 25px;
  box-sizing: border-box;
}

.song-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.song-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-artist {
  font-size: 13px;
  color: #cccccc;
  margin: 0;
}

.song-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.difficulties {
  display: flex;
  gap: 6px;
}

.uploader {
  font-size: 13px;
  color: #aaaaaa;
  min-width: 100px;
  text-align: right;
}

.uploader a {
  color: #00d4ff;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.uploader a:hover {
  color: #66e5ff;
}
</style>