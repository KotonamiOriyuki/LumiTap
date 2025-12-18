<!--Created: 19:30-->
<!--Ver 1.0-->
<!--Controlling grid of cells-->
<template>
  <div class="game-grid">
    <GameCell
      v-for="(cell, index) in cells"
      :key="index"
      :index="index"
      :state="cell.state"
      :opacity="cell.opacity"
      :text="cell.text"
      @cell-press="handleCellPress"
    />
  </div>
</template>

<script setup>
import GameCell from './GameCell.vue'

defineProps({
  cells: Array
})

const emit = defineEmits(['cell-press'])

const handleCellPress = (index) => {
  emit('cell-press', index)
}
</script>

<style scoped>
.game-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  width: 500px;
  height: 500px;
}
</style>