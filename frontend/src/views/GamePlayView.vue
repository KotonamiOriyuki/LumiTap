<!--Created: Dec 15, 21:00-->
<!--Ver 1.1-->
<!--The main playing page-->
<!--Changed: Dec 17, Change to WebAudioAPI and music loading animation-->
<template>
  <div class="gameplay-view" :style="{ backgroundImage: `url(${beatmapInfo?.background})` }">
    <div class="gameplay-overlay">
      <div class="loading-screen" v-if="!isReady">
        <div class="loading-content">
          <div class="loading-title">{{ beatmapInfo?.title || 'Loading...' }}</div>
          <div class="loading-artist">{{ beatmapInfo?.artist }}</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: loadProgress + '%' }"></div>
          </div>
          <div class="progress-text">{{ loadProgress.toFixed(0) }}%</div>
        </div>
      </div>

      <template v-else>
        <div class="game-header">
          <div class="header-left">
            <div class="diff-badge" :style="diffStyle">
              {{ diffInfo?.name }} {{ diffInfo?.level }}
            </div>
            <span class="song-info">{{ beatmapInfo?.title }} - {{ beatmapInfo?.artist }}</span>
          </div>
          <div class="header-right">
            <div class="score-display">{{ currentScore.toLocaleString() }}</div>
            <div class="accuracy-display">{{ currentAccuracy.toFixed(2) }}%</div>
          </div>
        </div>

        <div class="game-content">
          <div class="combo-display" v-if="combo > 0">{{ combo }}x</div>
          <div class="game-grid" ref="gridRef">
            <div
                v-for="(cell, index) in cells"
                :key="index"
                class="game-cell"
                :class="{ active: cell.state !== 'idle' }"
                :style="getCellStyle(cell)"
                @touchstart.prevent="handleCellInput(index)"
                @mousedown.left.prevent="handleCellInput(index)"
            >
              <span v-if="cell.text" class="cell-text">{{ cell.text }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../utils/api'
import { getDifficultyStyle, calculateScore, getRank } from '../utils/scoring.js'

const route = useRoute()
const router = useRouter()

const beatmapInfo = ref(null)
const diffInfo = ref(null)
const chartData = ref(null)

// Rongze Fan: loading
const isReady = ref(false)
const loadProgress = ref(0)

// Rongze Fan: webAudioAPI variables
let audioContext = null
let audioBuffer = null
let audioSource = null
let audioStartTime = 0

const cells = reactive(Array(16).fill(null).map(() => ({
  state: 'idle',
  opacity: 0,
  text: ''
})))

const currentScore = ref(0)
const currentAccuracy = ref(100)
const combo = ref(0)
const maxCombo = ref(0)
const greatCount = ref(0)
const goodCount = ref(0)
const missCount = ref(0)
const totalNotes = ref(0)

const activeNotes = ref([])
const isPlaying = ref(false)
let animationId = null

// Zixiao Shen: The main keymap binding of cells
const keyMap = {
  '1': 0, '2': 1, '3': 2, '4': 3,
  'q': 4, 'w': 5, 'e': 6, 'r': 7,
  'a': 8, 's': 9, 'd': 10, 'f': 11,
  'z': 12, 'x': 13, 'c': 14, 'v': 15
}

// Rongze Fan: Animation settings
const FADE_IN_DURATION = 160
const JUDGMENT_OFFSET = 140

const diffStyle = computed(() => {
  if (!diffInfo.value) return {}
  const style = getDifficultyStyle(diffInfo.value.level)
  return { backgroundColor: style.bg, color: style.text }
})

const getCellStyle = (cell) => {
  let bgColor = 'transparent'
  let borderColor = 'rgba(255, 255, 255, 0.3)'

  switch (cell.state) {
    case 'tap':
      bgColor = `rgba(0, 188, 212, ${cell.opacity})`
      borderColor = '#00bcd4'
      break
    case 'great':
      bgColor = `rgba(255, 152, 0, ${cell.opacity})`
      borderColor = '#ff9800'
      break
    case 'good':
      bgColor = `rgba(76, 175, 80, ${cell.opacity})`
      borderColor = '#4caf50'
      break
    case 'miss':
      bgColor = `rgba(244, 67, 54, ${cell.opacity})`
      borderColor = '#f44336'
      break
  }

  return { backgroundColor: bgColor, borderColor }
}

// Rongze Fan: fetch precise game time
const getCurrentTime = () => {
  if (!audioContext || !audioStartTime) return 0
  return (audioContext.currentTime - audioStartTime) * 1000
}

// Rongze Fan: added realtime score refresh
const updateScoreDisplay = () => {
  const total = greatCount.value + goodCount.value + missCount.value
  if (total === 0) {
    currentAccuracy.value = 100
    currentScore.value = 0
    return
  }

  const result = calculateScore(
      greatCount.value,
      goodCount.value,
      missCount.value,
      maxCombo.value,
      totalNotes.value
  )
  currentScore.value = result.score
  currentAccuracy.value = result.accuracy
}

// Chenxi Liu: Touching supports
// Rongze Fan: Change the function name
const handleCellInput = (cellIndex) => {
  if (!isPlaying.value) return

  const currentTime = getCurrentTime()

  const noteIndex = activeNotes.value.findIndex(n => n.cell === cellIndex && !n.hit && !n.missed)
  if (noteIndex === -1) return

  const note = activeNotes.value[noteIndex]
  const diff = Math.abs(currentTime - note.time)

  if (diff <= 140) {
    note.hit = true
    greatCount.value++
    combo.value++
    if (combo.value > maxCombo.value) maxCombo.value = combo.value
    showFeedback(cellIndex, 'great', 'Great!')
  } else if (diff <= 300) {
    note.hit = true
    goodCount.value++
    combo.value++
    if (combo.value > maxCombo.value) maxCombo.value = combo.value
    showFeedback(cellIndex, 'good', 'Good')
  }

  updateScoreDisplay()
}

const handleKeyDown = (e) => {
  if (!isPlaying.value) return
  if (e.repeat) return

  const key = e.key.toLowerCase()
  const cellIndex = keyMap[key]
  if (cellIndex === undefined) return

  handleCellInput(cellIndex)
}

const showFeedback = (cellIndex, state, text) => {
  cells[cellIndex].state = state
  cells[cellIndex].opacity = 1
  cells[cellIndex].text = text

  let opacity = 1
  const fade = () => {
    opacity -= 0.1
    if (opacity <= 0) {
      cells[cellIndex].state = 'idle'
      cells[cellIndex].opacity = 0
      cells[cellIndex].text = ''
    } else {
      cells[cellIndex].opacity = opacity
      // Rongze Fan: use requestAnimationFrame to ensure efficient animation
      requestAnimationFrame(fade)
    }
  }

  setTimeout(() => requestAnimationFrame(fade), 75)
}


const gameLoop = () => {
  if (!isPlaying.value) return

  // Rongze Fan: Adjustment to the changable time
  const currentTime = getCurrentTime()
  const JUDGMENT_WINDOW_END = -300
  const GREAT_END = -140
  const GOOD_END = -300

  if (audioBuffer && currentTime >= audioBuffer.duration * 1000 + 500) {
    handleGameEnd()
    return
  }

  for (let i = 0; i < activeNotes.value.length; i++) {
    const note = activeNotes.value[i]
    if (note.hit || note.missed) continue

    const timeDiff = note.time - currentTime

    const fadeStart = JUDGMENT_OFFSET + FADE_IN_DURATION
    const fadeEnd = JUDGMENT_OFFSET

    if (timeDiff <= fadeStart && timeDiff > fadeEnd) {
      const progress = 1 - (timeDiff - fadeEnd) / FADE_IN_DURATION
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = progress
      cells[note.cell].text = ''

    } else if (timeDiff <= fadeEnd && timeDiff >= GREAT_END) {
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = 1
      cells[note.cell].text = 'Tap!'

    } else if (timeDiff < GREAT_END && timeDiff >= GOOD_END) {
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = 1
      cells[note.cell].text = 'Tap!'

    } else if (timeDiff < JUDGMENT_WINDOW_END && !note.missed) {
      note.missed = true
      missCount.value++
      combo.value = 0
      showFeedback(note.cell, 'miss', 'Miss!')
      updateScoreDisplay()
    }
  }

  animationId = requestAnimationFrame(gameLoop)
}

// Rongze Fan: use webAudioAPI to ensure the precise playing time management
const loadAudio = async (url) => {
  audioContext = new (window.AudioContext || window.webkitAudioContext)()

  const response = await fetch(url)
  const total = parseInt(response.headers.get('content-length') || '0')
  const reader = response.body.getReader()

  let received = 0
  const chunks = []

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    chunks.push(value)
    received += value.length

    if (total > 0) {
      loadProgress.value = (received / total) * 100
    } else {
      loadProgress.value = Math.min(loadProgress.value + 10, 90)
    }
  }

  const arrayBuffer = new Uint8Array(received)
  let position = 0
  for (const chunk of chunks) {
    arrayBuffer.set(chunk, position)
    position += chunk.length
  }

  loadProgress.value = 95
  audioBuffer = await audioContext.decodeAudioData(arrayBuffer.buffer)
  loadProgress.value = 100
}

const handleGameEnd = async () => {
  if (!isPlaying.value) return
  isPlaying.value = false

  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }

  activeNotes.value.forEach(note => {
    if (!note.hit && !note.missed) {
      note.missed = true
      missCount.value++
    }
  })
  updateScoreDisplay()

  const rank = getRank(currentAccuracy.value)

  try {
    await api.post('/scores/submit', {
      bid: route.params.bid,
      score: currentScore.value,
      accuracy: currentAccuracy.value,
      great_count: greatCount.value,
      good_count: goodCount.value,
      miss_count: missCount.value,
      max_combo: maxCombo.value
    })
  } catch (e) {
    console.error('Failed to submit score')
  }

  sessionStorage.setItem('gameResult', JSON.stringify({
    bid: route.params.bid,
    score: currentScore.value,
    accuracy: currentAccuracy.value,
    rank,
    greatCount: greatCount.value,
    goodCount: goodCount.value,
    missCount: missCount.value,
    maxCombo: maxCombo.value
  }))
  router.push(`/result/${route.params.bid}`)
}

const startGame = () => {
  if (!chartData.value || !audioBuffer) return

  activeNotes.value = chartData.value.notes.map((note, index) => ({
    id: index,
    time: note.time,
    cell: note.cell,
    hit: false,
    missed: false
  }))

  totalNotes.value = activeNotes.value.length
  isPlaying.value = true

  audioSource = audioContext.createBufferSource()
  audioSource.buffer = audioBuffer
  audioSource.connect(audioContext.destination)
  audioSource.onended = handleGameEnd

  audioStartTime = audioContext.currentTime
  audioSource.start(0)

  gameLoop()
}

// Rongze Fan: waiting until all critical parts are loaded
const init = async () => {
  try {
    const res = await api.get(`/beatmaps/difficulty/${route.params.bid}`)
    diffInfo.value = res.data
    beatmapInfo.value = res.data.beatmap
    chartData.value = res.data.chart_data

    await loadAudio(beatmapInfo.value.audio)

    isReady.value = true

    setTimeout(startGame, 500)
  } catch (e) {
    console.error('Failed to load difficulty')
  }
}


onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  init()
})

onUnmounted(() => {
  isPlaying.value = false
  window.removeEventListener('keydown', handleKeyDown)

  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  if (audioSource) {
    try {
      audioSource.stop()
    } catch (e) {}
  }

  if (audioContext) {
    audioContext.close()
  }
})
</script>

<style scoped>
.gameplay-view {
  width: 100vw;
  height: 100vh;
  background-size: cover;
  background-position: center;
}

.gameplay-overlay {
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
}

/* Rongze Fan: Loading Style */
.loading-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  text-align: center;
  width: 300px;
}

.loading-title {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 8px;
}

.loading-artist {
  font-size: 16px;
  color: #aaaaaa;
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #333333;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #00d4ff;
  transition: width 0.1s ease-out;
}

.progress-text {
  margin-top: 10px;
  font-size: 14px;
  color: #888888;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.diff-badge {
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.song-info {
  font-size: 16px;
  color: #ffffff;
}

.header-right {
  text-align: right;
}

/* Rongze Fan: Score display style */
.score-display {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
}

.accuracy-display {
  font-size: 16px;
  color: #cccccc;
}

.game-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.combo-display {
  position: absolute;
  bottom: 30px;
  left: 30px;
  font-size: 32px;
  font-weight: bold;
  color: #ffffff;
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  width: min(450px, 90vw);
  height: min(450px, 90vw);
  touch-action: none;
  user-select: none;
}

.game-cell {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  will-change: background-color, border-color;

  /* Rongze Fan: blur style */
  background-color: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* Rongze Fan: activated animations */

.game-cell.active {
  transition: none;
}

.game-cell:active {
  transform: scale(0.95);
}

.cell-text {
  font-size: 22px;
  font-weight: bold;
  color: rgba(0, 0, 0, 0.7);
  pointer-events: none;
}
</style>