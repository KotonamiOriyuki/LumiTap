<!--Created Dec 14, 23:00-->
<!--Ver 1.0-->
<!--Views of song list-->
<template>
  <div class="songs-view">
    <div class="songs-container">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search songs..."
          @input="handleSearchInput"
        />
      </div>
      <div class="songs-list" v-if="songs.length > 0">
        <SongCard v-for="song in songs" :key="song.sid" :song="song" />
      </div>
      <div class="no-results" v-else>
        暂无
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import SongCard from '../components/SongCard.vue'

const searchQuery = ref('')
const songs = ref([])
let searchTimeout = null

const searchSongs = async () => {
  try {
    const res = await api.get('/beatmaps/search', { params: { q: searchQuery.value } })
    songs.value = res.data
  } catch (e) {
    console.error('Search failed')
  }
}

// Chenxi Liu: lazy searching, the searching process started since no input within 0.5s
const handleSearchInput = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    searchSongs()
  }, 500)
}

onMounted(() => {
  searchSongs()
})
</script>

<style scoped>
.songs-view {
  min-height: calc(100vh - 50px);
  padding: 30px;
}

.songs-container {
  max-width: 1200px;
  margin: 0 auto;
}

.search-box {
  display: flex;
  align-items: center;
  background-color: #2a2a2a;
  border-radius: 7px;
  padding: 12px 20px;
  margin-bottom: 25px;
}

.search-icon {
  margin-right: 15px;
  font-size: 18px;
}

.search-box input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 16px;
  font-family: 'MiSans', sans-serif;
}

.search-box input::placeholder {
  color: #666666;
}

.songs-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.no-results {
  text-align: center;
  color: #666666;
  font-size: 18px;
  padding: 50px;
}
</style>