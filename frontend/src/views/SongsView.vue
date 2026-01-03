<!--Created Dec 14, 23:00-->
<!--Ver 1.1-->
<!--Views of song list-->
<!--Changelog: Jan 3, 2026: Add offset settings and basic songs filter-->
<template>
  <div class="songs-view">
    <div class="songs-container">
      <div class="search-header">
        <div class="search-box">
          <input
              v-model="searchQuery"
              type="text"
              placeholder="Search songs..."
              @input="handleSearchInput"
          />
        </div>
        <div class="filter-wrapper">
          <button class="filter-toggle-btn" @click="showFilters = !showFilters">
            <span class="filter-icon">⚙️</span>
          </button>
          <div v-if="showFilters" class="filter-dropdown">
            <div class="filter-section">
              <div class="filter-label">Difficulty Range</div>
              <div class="filter-inputs">
                <input v-model.number="filters.minDiff" type="number" placeholder="Min" />
                <span class="sep">-</span>
                <input v-model.number="filters.maxDiff" type="number" placeholder="Max" />
              </div>
            </div>
            <div class="filter-section">
              <div class="filter-label">BPM Range</div>
              <div class="filter-inputs">
                <input v-model.number="filters.minBpm" type="number" placeholder="Min" />
                <span class="sep">-</span>
                <input v-model.number="filters.maxBpm" type="number" placeholder="Max" />
              </div>
            </div>
<!--     Zheng Wu: Offset setups, beep and calculate their differences       -->
            <div class="filter-section">
              <button class="offset-setup-btn" @click="openOffsetModal">Offset Settings</button>
            </div>
            <div class="filter-actions">
              <button class="reset-btn" @click="resetFilters">Reset</button>
              <button class="apply-btn" @click="showFilters = false">Close</button>
            </div>
          </div>
        </div>
      </div>

      <div class="songs-list" v-if="filteredSongs.length > 0">
        <SongCard v-for="song in filteredSongs" :key="song.sid" :song="song" />
      </div>
      <div class="no-results" v-else>
        None
      </div>
    </div>

    <div v-if="showOffsetModal" class="offset-modal">
      <div class="offset-modal-content">
        <h3>Calibration</h3>
        <p class="instruction">Click immediately when hearing the sound</p>
        <p class="offset-display">Average Offset: {{ currentAverageOffset.toFixed(1) }}ms</p>
        <div class="click-area">
          <button class="click-btn" @mousedown="handleOffsetClick">Click</button>
        </div>
        <div class="modal-actions">
          <button @click="saveOffset">Save</button>
          <button @click="closeOffsetModal">Cancel</button>
          <button @click="resetUserOffset">Reset</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import api from '../utils/api'
import SongCard from '../components/SongCard.vue'

const searchQuery = ref('')
const songs = ref([])
const showFilters = ref(false)
const filters = reactive({
  minDiff: null,
  maxDiff: null,
  minBpm: null,
  maxBpm: null
})

// Offset logic state
const showOffsetModal = ref(false)
const offsetSamples = ref([])
const intervalMs = 800
let offsetAudioCtx = null
let nextDingTime = 0
let dingInterval = null

const currentAverageOffset = computed(() => {
  if (offsetSamples.value.length === 0) return 0
  return offsetSamples.value.reduce((a, b) => a + b, 0) / offsetSamples.value.length
})

const openOffsetModal = () => {
  showOffsetModal.value = true
  offsetSamples.value = []
  startDingLoop()
}

const startDingLoop = () => {
  offsetAudioCtx = new (window.AudioContext || window.webkitAudioContext)()
  const playDing = () => {
    const osc = offsetAudioCtx.createOscillator()
    const gain = offsetAudioCtx.createGain()
    osc.type = 'sine'
    osc.frequency.setValueAtTime(880, offsetAudioCtx.currentTime)
    gain.gain.setValueAtTime(0.5, offsetAudioCtx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, offsetAudioCtx.currentTime + 0.1)
    osc.connect(gain)
    gain.connect(offsetAudioCtx.destination)
    osc.start()
    osc.stop(offsetAudioCtx.currentTime + 0.1)
    nextDingTime = Date.now()
  }
  playDing()
  dingInterval = setInterval(playDing, intervalMs)
}

const handleOffsetClick = () => {
  const now = Date.now()
  let diff = now - nextDingTime
  if (diff > intervalMs / 2) diff -= intervalMs
  if (Math.abs(diff) <= 50) offsetSamples.value.push(diff)
}

const saveOffset = async () => {
  try {
    await api.put('/users/me', { offset: currentAverageOffset.value })
    closeOffsetModal()
  } catch (e) { console.error('Failed to save offset') }
}

const resetUserOffset = async () => {
  try {
    await api.put('/users/me', { offset: 0 })
    offsetSamples.value = []
  } catch (e) { console.error('Failed to reset offset') }
}

const closeOffsetModal = () => {
  showOffsetModal.value = false
  if (dingInterval) clearInterval(dingInterval)
  if (offsetAudioCtx) offsetAudioCtx.close()
}

let searchTimeout = null

// Zheng Wu: transferred to the backend
const searchSongs = async () => {
  try {
    const res = await api.get('/beatmaps/search', { params: { q: searchQuery.value } })
    songs.value = res.data
  } catch (e) {
    console.error('Search failed')
  }
}

const filteredSongs = computed(() => {
  return songs.value.filter(song => {
    const bpmMatch = (!filters.minBpm || song.bpm >= filters.minBpm) &&
        (!filters.maxBpm || song.bpm <= filters.maxBpm)

    const diffMatch = !filters.minDiff && !filters.maxDiff ||
        song.difficulties.some(d => {
          const minOk = !filters.minDiff || d.level >= filters.minDiff
          const maxOk = !filters.maxDiff || d.level <= filters.maxDiff
          return minOk && maxOk
        })

    return bpmMatch && diffMatch
  })
})

const handleSearchInput = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    searchSongs()
  }, 500)
}

const resetFilters = () => {
  filters.minDiff = null
  filters.maxDiff = null
  filters.minBpm = null
  filters.maxBpm = null
}

onMounted(() => {
  searchSongs()
})

onUnmounted(() => {
  closeOffsetModal()
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

.search-header {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  position: relative;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: #2a2a2a;
  border-radius: 7px;
  padding: 12px 20px;
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

.filter-wrapper {
  position: relative;
}

.filter-toggle-btn {
  height: 100%;
  background-color: #2a2a2a;
  border: none;
  border-radius: 7px;
  color: #ffffff;
  padding: 0 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: background-color 0.2s;
}

.filter-toggle-btn:hover {
  background-color: #3a3a3a;
}

.filter-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 280px;
  background-color: #2a2a2a;
  border-radius: 7px;
  padding: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  z-index: 100;
  border: 1px solid #3a3a3a;
}

.filter-section {
  margin-bottom: 15px;
}

.filter-label {
  font-size: 12px;
  color: #888888;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.filter-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-inputs input {
  width: 100%;
  background-color: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  padding: 8px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
}

.filter-inputs input:focus {
  border-color: #00d4ff;
}

.sep {
  color: #666666;
}

.offset-setup-btn {
  width: 100%;
  background-color: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  padding: 8px;
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #3a3a3a;
}

.reset-btn, .apply-btn {
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  border: none;
}

.reset-btn {
  background-color: transparent;
  color: #888888;
}

.apply-btn {
  background-color: #00d4ff;
  color: #1a1a1a;
  font-weight: bold;
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

/* Modal styles */
.offset-modal {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.offset-modal-content {
  background: #2a2a2a; padding: 40px; border-radius: 12px;
  text-align: center; max-width: 400px; width: 90%;
}
.instruction { color: #aaa; margin: 20px 0; }
.offset-display { color: #00d4ff; font-weight: bold; margin-bottom: 20px; }
.click-btn {
  width: 120px; height: 120px; border-radius: 50%;
  background: #00d4ff; border: none; font-weight: bold; font-size: 18px;
  cursor: pointer; box-shadow: 0 0 20px rgba(0,212,255,0.4);
}
.click-btn:active { transform: scale(0.95); }
.modal-actions { display: flex; gap: 10px; justify-content: center; margin-top: 30px; }
.modal-actions button {
  padding: 10px 20px; border-radius: 6px; border: none; cursor: pointer;
}

@media (max-width: 768px) {
  .songs-view {
    padding: 15px;
  }
  .search-header {
    flex-direction: row;
    gap: 10px;
  }
  .search-box {
    padding: 10px 15px;
  }
  .filter-toggle-btn {
    padding: 0 15px;
  }
  .filter-dropdown {
    width: calc(100vw - 30px);
    right: 0;
    position: absolute;
  }
}
</style>