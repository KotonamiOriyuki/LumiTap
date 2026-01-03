<!--Created: Dec 15, 21:00-->
<!--Ver 1.2-->
<!--The main playing page-->
<!--Changed: Dec 17, Change to WebAudioAPI and music loading animation-->
<!--Changed: Jan 1, optimized the combo animation, added full combo/all great animation, add pause option-->
<template>
  <div class="gameplay-view" :style="{ backgroundImage: `url(${beatmapInfo?.background})` }">
    <div class="gameplay-overlay" :class="{ 'paused-blur': isPaused }">
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
        <div class="song-progress-bar">
          <div class="song-progress-fill" :style="{ width: songProgress + '%' }"></div>
        </div>

        <div class="game-header">
          <div class="header-left">
            <div class="diff-badge" :style="diffStyle" @click="pauseGame">
              {{ diffInfo?.name }} {{ diffInfo?.level }}
            </div>
            <span class="song-info">{{ beatmapInfo?.title }} - {{ beatmapInfo?.artist }}</span>
          </div>
          <div class="header-right">
            <div class="score-display">{{ Math.round(currentScore).toLocaleString() }}</div>
            <div class="accuracy-display">{{ currentAccuracy.toFixed(2) }}%</div>
          </div>
        </div>

        <div class="game-content">
<!--          Rongze Fan: change the combo overlay to the middle of the game grid  -->
          <div class="combo-layer">
            <div v-for="p in particles" :key="p.id" class="particle" :style="getParticleStyle(p)">。</div>
            <div class="combo-container" v-if="combo > 0">
              <div class="combo-number" :key="combo">{{ combo }}</div>
            </div>
          </div>
          <div
              class="game-grid"
              ref="gridRef"
              @touchstart.prevent="handleTouchStart"
              @touchmove.prevent="handleTouchMove"
              @touchend.prevent="handleTouchEnd"
              @touchcancel.prevent="handleTouchCancel"
          >
            <div
                v-for="(cell, index) in cells"
                :key="index"
                class="game-cell"
                :class="{ active: cell.state !== 'idle' }"
                :style="getCellStyle(cell)"
                :data-index="index"
                @mousedown.left.prevent="handleCellInput(index)"
            >
              <span v-if="cell.text" class="cell-text" :class="cell.state">{{ cell.text }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!--          Rongze Fan: three options when paused  -->
    <div class="pause-overlay" v-if="isPaused">
      <div class="pause-content">
        <div class="pause-title">Paused</div>
        <div class="pause-buttons">
          <button class="pause-btn" @click="handleContinue">Continue</button>
          <button class="pause-btn" @click="handleRestart">Restart</button>
          <button class="pause-btn" @click="handleBack">Back</button>
        </div>
      </div>
    </div>

    <div class="countdown-overlay" v-if="isCountingDown">
      <div class="countdown-inner">
        <div class="countdown-number">{{ countdownValue }}</div>
        <div class="countdown-bar">
          <div class="countdown-fill" :style="{ width: countdownProgress + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDifficultyStyle, calculateScore, getRank } from '../utils/scoring'
import api from '../utils/api'

const route = useRoute()
const router = useRouter()

const beatmapInfo = ref(null)
const diffInfo = ref(null)
const chartData = ref(null)
const gridRef = ref(null)
const userOffset = ref(0) // Variable to hold user's personal timing offset

// Rongze Fan: loading
const isReady = ref(false)
const loadProgress = ref(0)

// Rongze Fan: pause related
const isPaused = ref(false)
const isCountingDown = ref(false)
const countdownValue = ref(3)
const countdownProgress = ref(100)
let pausedTime = 0
let countdownTimer = null

const songProgress = ref(0)
const activeTouches = new Map()

// Rongze Fan: webAudioAPI variables
let audioContext = null
let audioBuffer = null
let audioSource = null
let audioStartTime = 0
let gameEnded = false

const cells = reactive(Array(16).fill(null).map(() => ({
  state: 'idle',
  opacity: 0,
  text: ''
})))

// Rongze Fan: particles for fc/ag animations
const particles = ref([])
let particleId = 0

const currentScore = ref(0)
const currentAccuracy = ref(100)
const combo = ref(0)
const maxCombo = ref(0)
const greatCount = ref(0)
const goodCount = ref(0)
const missCount = ref(0)
const totalNotes = ref(0)
const comboScore = ref(0)

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
const config = reactive({
  great: 140,
  good: 300,
  fadeIn: 160,
  offset: 140
})

const diffStyle = computed(() => {
  if (!diffInfo.value) return {}
  const style = getDifficultyStyle(diffInfo.value.level)
  return { backgroundColor: style.bg, color: style.text }
})

const getCellStyle = (cell) => {
  let bgColor = 'transparent'
  let borderColor = 'rgba(255, 255, 255, 0.2)'
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

// Rongze Fan: Animations for full combo / all great
const createParticles = (type) => {
  const count = 30
  const colors = ['#ff8a80', '#ffd180', '#80d8ff', '#b9f6ca', '#ea80fc']
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 / count) * i + Math.random() * 0.5
    const speed = 2 + Math.random() * 4
    particles.value.push({
      id: particleId++,
      x: 0,
      y: 0,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      size: 60 + Math.random() * 80,
      color: type === 'allGreat' ? colors[Math.floor(Math.random() * colors.length)] : '#ffffff',
      life: 1.0
    })
  }
}

const updateParticles = () => {
  for (let i = particles.value.length - 1; i >= 0; i--) {
    const p = particles.value[i]
    p.x += p.vx
    p.y += p.vy
    p.life -= 0.012
    if (p.life <= 0) {
      particles.value.splice(i, 1)
    }
  }
}

const getParticleStyle = (p) => {
  return {
    transform: `translate(-50%, -50%) translate(${p.x}px, ${p.y}px) scale(${p.life})`,
    color: p.color,
    fontSize: `${p.size}px`,
    opacity: p.life * 0.4
  }
}

// Rongze Fan: fetch precise game time
const getCurrentTime = () => {
  if (!audioContext || !audioStartTime) return 0
  return (audioContext.currentTime - audioStartTime) * 1000
}

// Rongze Fan: the progress bar on the top
const updateSongProgress = () => {
  if (!audioBuffer) return
  const currentTime = getCurrentTime()
  const duration = audioBuffer.duration * 1000
  songProgress.value = Math.min(100, Math.max(0, (currentTime / duration) * 100))
}

// Rongze Fan: multi-touch support and judgement rewrite
const handleCellInput = (cellIndex) => {
  if (!isPlaying.value || isPaused.value || isCountingDown.value) return
  const currentTime = getCurrentTime()
  const noteIndex = activeNotes.value.findIndex(n => n.cell === cellIndex && !n.hit && !n.missed)
  if (noteIndex === -1) return
  const note = activeNotes.value[noteIndex]
  const diff = Math.abs(currentTime - note.time)
  let judgment = ''
  if (diff <= config.great) {
    judgment = 'great'
    greatCount.value++
    combo.value++
    showFeedback(cellIndex, 'great', 'Great!')
  } else if (diff <= config.good) {
    judgment = 'good'
    goodCount.value++
    combo.value++
    showFeedback(cellIndex, 'good', 'Good')
  } else {
    return
  }

  note.hit = true

  if (combo.value > maxCombo.value) maxCombo.value = combo.value
  const { accInc, comboInc } = calculateScore(judgment, totalNotes.value, combo.value)
  currentScore.value += (accInc + comboInc)
  const totalJudgments = greatCount.value + goodCount.value + missCount.value
  currentAccuracy.value = ((greatCount.value * 100 + goodCount.value * 50) / (totalJudgments * 100)) * 100

  if (greatCount.value === totalNotes.value) {
    createParticles('allGreat')
  } else if (greatCount.value + goodCount.value === totalNotes.value) {
    createParticles('fullCombo')
  }
}

const getCellIndexFromTouch = (touch) => {
  if (!gridRef.value) return -1
  const element = document.elementFromPoint(touch.clientX, touch.clientY)
  if (!element) return -1
  const cell = element.closest('.game-cell')
  if (!cell) return -1
  const index = parseInt(cell.dataset.index)
  return isNaN(index) ? -1 : index
}

const handleTouchStart = (e) => {
  if (!isPlaying.value || isPaused.value || isCountingDown.value) return
  for (const touch of e.changedTouches) {
    const cellIndex = getCellIndexFromTouch(touch)
    if (cellIndex >= 0 && !activeTouches.has(touch.identifier)) {
      activeTouches.set(touch.identifier, cellIndex)
      handleCellInput(cellIndex)
    }
  }
}

const handleTouchMove = (e) => {
  if (!isPlaying.value || isPaused.value || isCountingDown.value) return
  for (const touch of e.changedTouches) {
    const newCellIndex = getCellIndexFromTouch(touch)
    const oldCellIndex = activeTouches.get(touch.identifier)
    if (newCellIndex >= 0 && newCellIndex !== oldCellIndex) {
      activeTouches.set(touch.identifier, newCellIndex)
      handleCellInput(newCellIndex)
    }
  }
}

const handleTouchEnd = (e) => {
  for (const touch of e.changedTouches) {
    activeTouches.delete(touch.identifier)
  }
}

const handleTouchCancel = (e) => {
  for (const touch of e.changedTouches) {
    activeTouches.delete(touch.identifier)
  }
}

// Rongze Fan: pause all animations and music playback
const pauseGame = () => {
  if (!isPlaying.value || isPaused.value || isCountingDown.value || gameEnded) return
  isPaused.value = true
  pausedTime = getCurrentTime()
  activeTouches.clear()
  if (audioSource) {
    try {
      audioSource.onended = null
      audioSource.stop()
    } catch (e) {}
    audioSource = null
  }
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
}

//Rongze Fan: 3 seconds coundown
const handleContinue = () => {
  if (isCountingDown.value) return
  isPaused.value = false
  isCountingDown.value = true
  countdownValue.value = 3
  countdownProgress.value = 100
  let remaining = 3000
  countdownTimer = setInterval(() => {
    remaining -= 50
    countdownProgress.value = (remaining / 3000) * 100
    countdownValue.value = Math.ceil(remaining / 1000)
    if (remaining <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
      isCountingDown.value = false
      resumeGame()
    }
  }, 50)
}

const resumeGame = () => {
  if (!audioBuffer || !audioContext || gameEnded) return
  audioSource = audioContext.createBufferSource()
  audioSource.buffer = audioBuffer
  audioSource.connect(audioContext.destination)
  audioSource.onended = onAudioEnded
  const resumePosition = (pausedTime + userOffset.value) / 1000
  audioStartTime = audioContext.currentTime - resumePosition
  audioSource.start(0, resumePosition)
  gameLoop()
}

const handleRestart = () => {
  window.location.reload()
}

const handleBack = () => {
  gameEnded = true
  isPlaying.value = false
  if (countdownTimer) clearInterval(countdownTimer)
  if (animationId) cancelAnimationFrame(animationId)
  if (audioSource) {
    try {
      audioSource.onended = null
      audioSource.stop()
    } catch (e) {}
  }
  if (audioContext) audioContext.close()
  const sid = beatmapInfo.value?.sid || diffInfo.value?.sid
  router.push(sid ? `/beatmap/${sid}` : '/songs')
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    e.preventDefault()
    if (isCountingDown.value) return
    isPaused.value ? handleContinue() : pauseGame()
    return
  }
  if (!isPlaying.value || isPaused.value || isCountingDown.value) return
  if (e.repeat) return
  const cellIndex = keyMap[e.key.toLowerCase()]
  if (cellIndex !== undefined) handleCellInput(cellIndex)
}

const showFeedback = (cellIndex, state, text) => {
  cells[cellIndex].state = state
  cells[cellIndex].opacity = 1
  cells[cellIndex].text = text
  let opacity = 1
  const fade = () => {
    if (isPaused.value || isCountingDown.value) {
      requestAnimationFrame(fade)
      return
    }
    opacity -= 0.05
    if (opacity <= 0) {
      cells[cellIndex].state = 'idle'
      cells[cellIndex].opacity = 0
      cells[cellIndex].text = ''
    } else {
      cells[cellIndex].opacity = opacity
      requestAnimationFrame(fade)
    }
  }
  setTimeout(() => requestAnimationFrame(fade), 75)
}

const gameLoop = () => {
  if (!isPlaying.value || isPaused.value || isCountingDown.value || gameEnded) return
  const currentTime = getCurrentTime()
  updateSongProgress()
  updateParticles()
  for (let i = 0; i < activeNotes.value.length; i++) {
    const note = activeNotes.value[i]
    if (note.hit || note.missed) continue
    const timeDiff = note.time - currentTime
    if (timeDiff <= config.offset + config.fadeIn && timeDiff > config.offset) {
      const progress = 1 - (timeDiff - config.offset) / config.fadeIn
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = progress
      cells[note.cell].text = ''
    } else if (timeDiff <= config.offset && timeDiff >= -config.great) {
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = 1
      cells[note.cell].text = 'Tap!'
    } else if (timeDiff < -config.great && timeDiff >= -config.good) {
      cells[note.cell].state = 'tap'
      cells[note.cell].opacity = 1
      cells[note.cell].text = 'Tap!'
    } else if (timeDiff < -config.good && !note.missed) {
      note.missed = true
      missCount.value++
      combo.value = 0
      showFeedback(note.cell, 'miss', 'Miss!')
      const totalJudgments = greatCount.value + goodCount.value + missCount.value
      currentAccuracy.value = ((greatCount.value * 100 + goodCount.value * 50) / (totalJudgments * 100)) * 100
    }
  }
  animationId = requestAnimationFrame(gameLoop)
}

const onAudioEnded = () => {
  if (!isPaused.value && !isCountingDown.value && !gameEnded) handleGameEnd()
}

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
    if (total > 0) loadProgress.value = (received / total) * 100
  }
  const arrayBuffer = new Uint8Array(received)
  let pos = 0
  for (const chunk of chunks) {
    arrayBuffer.set(chunk, pos)
    pos += chunk.length
  }
  audioBuffer = await audioContext.decodeAudioData(arrayBuffer.buffer)
  loadProgress.value = 100
}
// Rongze Fan: game init
const startGame = () => {
  if (!chartData.value || !audioBuffer) return
  gameEnded = false
  songProgress.value = 0
  activeNotes.value = chartData.value.notes.map((note, index) => ({
    id: index, time: note.time, cell: note.cell, hit: false, missed: false
  }))
  totalNotes.value = activeNotes.value.length
  isPlaying.value = true
  comboScore.value = 0
  audioSource = audioContext.createBufferSource()
  audioSource.buffer = audioBuffer
  audioSource.connect(audioContext.destination)
  audioSource.onended = onAudioEnded
  audioStartTime = audioContext.currentTime
  audioSource.start(0)
  gameLoop()
}

const handleGameEnd = async () => {
  if (gameEnded || isPaused.value || isCountingDown.value) return
  gameEnded = true
  isPlaying.value = false
  if (animationId) cancelAnimationFrame(animationId)
  activeNotes.value.forEach(n => { if (!n.hit && !n.missed) { n.missed = true; missCount.value++; } })

  const rank = getRank(currentAccuracy.value)
  try {
    await api.post('/scores/submit', {
      bid: route.params.bid,
      score: Math.round(currentScore.value),
      accuracy: currentAccuracy.value,
      great_count: greatCount.value,
      good_count: goodCount.value,
      miss_count: missCount.value,
      max_combo: maxCombo.value
    })
  } catch (e) {}
  sessionStorage.setItem('gameResult', JSON.stringify({
    bid: route.params.bid, score: Math.round(currentScore.value), accuracy: currentAccuracy.value,
    rank, greatCount: greatCount.value, goodCount: goodCount.value, missCount: missCount.value, maxCombo: maxCombo.value
  }))
  setTimeout(() => {
    router.push(`/result/${route.params.bid}`)
  }, 1200)
}

const init = async () => {
  try {
    const userRes = await api.get('/users/me')
    userOffset.value = userRes.data.offset || 0
    console.log(userOffset.value)

    const res = await api.get(`/beatmaps/difficulty/${route.params.bid}`)
    diffInfo.value = res.data
    beatmapInfo.value = res.data.beatmap
    chartData.value = res.data.chart_data
    const lvl = diffInfo.value.level
    if (lvl < 5) {
      config.great = 280
      config.good = 500
      config.fadeIn = 300
      config.offset = 250
    } else if (lvl >= 9) {
      config.great = 110
      config.good = 220
      config.fadeIn = 145
      config.offset = 110
    } else {
      config.great = 140
      config.good = 300
      config.fadeIn = 160
      config.offset = 140
    }
    await loadAudio(beatmapInfo.value.audio)
    isReady.value = true
    setTimeout(startGame, 500)
  } catch (e) {}
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  init()
})

onUnmounted(() => {
  gameEnded = true
  isPlaying.value = false
  window.removeEventListener('keydown', handleKeyDown)
  if (countdownTimer) clearInterval(countdownTimer)
  if (animationId) cancelAnimationFrame(animationId)
  if (audioSource) { try { audioSource.onended = null; audioSource.stop(); } catch (e) {} }
  if (audioContext) audioContext.close()
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
  transition: filter 0.3s ease;
}

.gameplay-overlay.paused-blur {
  filter: blur(10px);
}

.song-progress-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: rgba(255, 255, 255, 0.2);
  z-index: 10;
}

.song-progress-fill {
  height: 100%;
  background-color: #00d4ff;
  transition: width 0.1s linear;
}

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
  margin-top: 4px;
  position: relative;
  z-index: 20;
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
  cursor: pointer;
  transition: transform 0.1s ease, opacity 0.1s ease;
}

.diff-badge:hover {
  opacity: 0.8;
}

.diff-badge:active {
  transform: scale(0.95);
}

.song-info {
  font-size: 16px;
  color: #ffffff;
}

.header-right {
  text-align: right;
}

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

.combo-layer {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  pointer-events: none;
}

.combo-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.combo-number {
  font-size: 120px;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.5);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  animation: heartBeat 0.6s infinite ease-in-out;
}

.particle {
  position: absolute;
  font-weight: bold;
  pointer-events: none;
  line-height: 1;
  user-select: none;
}

@keyframes heartBeat {
  0% { transform: scale(1); opacity: 0.2; }
  20% { transform: scale(1.05); opacity: 0.3; }
  100% { transform: scale(1); opacity: 0.2; }
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
  position: relative;
  z-index: 10;
}

.game-cell {
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  will-change: background-color, border-color;
  background-color: transparent;
}

.cell-text {
  font-size: 24px;
  font-weight: bold;
  pointer-events: none;
  color: rgba(0, 0, 0, 0.7);
  text-shadow: none;
}

.pause-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  background-color: rgba(0, 0, 0, 0.3);
}

.pause-content {
  text-align: center;
}

.pause-title {
  font-size: 72px;
  font-weight: bold;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  margin-bottom: 60px;
  letter-spacing: 8px;
}

.pause-buttons {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.pause-btn {
  width: 200px;
  padding: 16px 40px;
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.countdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 150;
  background-color: rgba(0, 0, 0, 0.5);
}

.countdown-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.countdown-number {
  font-size: 120px;
  font-weight: bold;
  color: #00d4ff;
  text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
  margin-bottom: 40px;
}

.countdown-bar {
  width: 300px;
  height: 8px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.countdown-fill {
  height: 100%;
  background-color: #00d4ff;
  transition: width 0.05s linear;
}
</style>