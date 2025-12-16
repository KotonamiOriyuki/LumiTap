<!--Created: Dec 15, 21:00-->
<!--Ver 1.0-->
<!--The main playing page-->
<template>
  <div class="gameplay-view" :style="{ backgroundImage: `url(${beatmapInfo?.background})` }">
    <div class="gameplay-overlay">
      <div class="game-header">
        <div class="header-left">
          <div class="diff-badge" :style="diffStyle">
            {{ diffInfo?.name }} {{ diffInfo?.level }}
          </div>
          <span class="song-info">{{ beatmapInfo?.title }} - {{ beatmapInfo?.artist }}</span>
        </div>
        <div class="header-right">
<!--          Rongze Fan: Added score display function to the gameplay page-->
          <div class="score-display">{{ currentScore.toLocaleString() }}</div>
          <div class="accuracy-display">{{ currentAccuracy.toFixed(2) }}%</div>
        </div>
      </div>

      <div class="game-content">
        <div class="combo-display" v-if="combo > 0">{{ combo }}x</div>
        <div class="game-grid">
          <div
              v-for="(cell, index) in cells"
              :key="index"
              class="game-cell"
              :style="getCellStyle(cell)"
              @touchstart.prevent="handleCellTouch(index)"
              @mousedown="handleCellTouch(index)"
          >
            <span v-if="cell.text" class="cell-text">{{ cell.text }}</span>
          </div>
        </div>
      </div>

      <audio ref="audioRef" :src="beatmapInfo?.audio" @ended="handleGameEnd"></audio>
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
const audioRef = ref(null)

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
const gameStartTime = ref(0)
const isPlaying = ref(false)

// Zixiao Shen: The main keymap binding of cells
const keyMap = {
  '1': 0, '2': 1, '3': 2, '4': 3,
  'q': 4, 'w': 5, 'e': 6, 'r': 7,
  'a': 8, 's': 9, 'd': 10, 'f': 11,
  'z': 12, 'x': 13, 'c': 14, 'v': 15
}

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
const handleCellTouch = (cellIndex) => {
  if (!isPlaying.value) return

  const currentTime = Date.now() - gameStartTime.value

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

  const key = e.key.toLowerCase()
  const cellIndex = keyMap[key]
  if (cellIndex === undefined) return

  handleCellTouch(cellIndex)
}

const showFeedback = (cellIndex, state, text) => {
  cells[cellIndex].state = state
  cells[cellIndex].opacity = 1
  cells[cellIndex].text = text

  const fadeOut = () => {
    let opacity = 1
    const interval = setInterval(() => {
      opacity -= 0.1
      if (opacity <= 0) {
        clearInterval(interval)
        cells[cellIndex].state = 'idle'
        cells[cellIndex].opacity = 0
        cells[cellIndex].text = ''
      } else {
        cells[cellIndex].opacity = opacity
      }
    }, 15)
  }

  setTimeout(fadeOut, 50)
}


const gameLoop = () => {
  if (!isPlaying.value) return

  const currentTime = Date.now() - gameStartTime.value
  const FADE_IN_DURATION = 300
  const JUDGMENT_OFFSET = 65

  activeNotes.value.forEach(note => {
    if (note.hit || note.missed) return

    const timeDiff = note.time - currentTime

    if (timeDiff <= (JUDGMENT_OFFSET + FADE_IN_DURATION) && timeDiff > JUDGMENT_OFFSET) {
      const progress = 1 - (timeDiff - JUDGMENT_OFFSET) / FADE_IN_DURATION
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = progress
      cells[note.cell].text = 'Tap!'

    } else if (timeDiff <= JUDGMENT_OFFSET && timeDiff >= -140) {
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = 1
      cells[note.cell].text = 'Tap!'

    } else if (timeDiff < -140 && timeDiff >= -300) {
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = 1
      cells[note.cell].text = 'Tap!'

    } else if (timeDiff < -300 && !note.missed) {
      note.missed = true
      missCount.value++
      combo.value = 0
      showFeedback(note.cell, 'miss', 'Miss!')
      updateScoreDisplay()
    }
  })

  requestAnimationFrame(gameLoop)
}

const handleGameEnd = async () => {
  isPlaying.value = false

  activeNotes.value.forEach(note => {
    if (!note.hit && !note.missed) {
      note.missed = true
      missCount.value++
    }
  })
  updateScoreDisplay()

  // Rongze Fan: added rank fetch
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
  if (!chartData.value || !audioRef.value) return

  activeNotes.value = chartData.value.notes.map((note, index) => ({
    id: index,
    time: note.time,
    cell: note.cell,
    hit: false,
    missed: false
  }))

  totalNotes.value = activeNotes.value.length
  isPlaying.value = true
  gameStartTime.value = Date.now()

  audioRef.value.play()
  gameLoop()
}

onMounted(async () => {
  try {
    const res = await api.get(`/beatmaps/difficulty/${route.params.bid}`)
    diffInfo.value = res.data
    beatmapInfo.value = res.data.beatmap
    chartData.value = res.data.chart_data

    setTimeout(startGame, 1000)
  } catch (e) {
    console.error('Failed to load difficulty')
  }

  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  isPlaying.value = false
  window.removeEventListener('keydown', handleKeyDown)
  if (audioRef.value) {
    audioRef.value.pause()
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
  transition: background-color 0.05s, border-color 0.05s;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.cell-text {
  font-size: 22px;
  font-weight: bold;
  color: rgba(0, 0, 0, 0.7);
  pointer-events: none;
}
</style>