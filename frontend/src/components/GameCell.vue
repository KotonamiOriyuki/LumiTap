<!--Created: Dec 19, 20:00-->
<!--Ver 1.0-->
<!--Judgement and animation of each cell-->
<template>
  <div
    class="game-cell"
    :style="cellStyle"
    @click="handleClick"
  >
    <span v-if="text" class="cell-text">{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  index: Number,
  state: String,
  opacity: Number,
  text: String
})

const emit = defineEmits(['cell-press'])

const cellStyle = computed(() => {
  let bgColor = 'transparent'
  let borderColor = 'rgba(255, 255, 255, 0.3)'

  switch (props.state) {
    case 'tap':
      bgColor = `rgba(0, 188, 212, ${props.opacity})`
      borderColor = '#00bcd4'
      break
    case 'great':
      bgColor = `rgba(255, 152, 0, ${props.opacity})`
      borderColor = '#ff9800'
      break
    case 'good':
      bgColor = `rgba(76, 175, 80, ${props.opacity})`
      borderColor = '#4caf50'
      break
    case 'miss':
      bgColor = `rgba(244, 67, 54, ${props.opacity})`
      borderColor = '#f44336'
      break
  }

  return {
    backgroundColor: bgColor,
    borderColor: borderColor
  }
})

const handleClick = () => {
  emit('cell-press', props.index)
}
</script>

<style scoped>
.game-cell {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.05s, border-color 0.05s;
  user-select: none;
}

.cell-text {
  font-size: 24px;
  font-weight: bold;
  color: rgba(0, 0, 0, 0.7);
}
</style>