<!--Created: Dec 14 23:00-->
<!--Ver 1.0-->
<!--Display badges for each difficulties-->
<template>
  <div class="difficulty-badge" :style="badgeStyle">
    {{ name }} {{ level }}
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getDifficultyStyle } from '../utils/scoring'

const props = defineProps({
  name: String,
  level: Number
})

const badgeStyle = computed(() => {
  const style = getDifficultyStyle(props.level)
  return {
    backgroundColor: style.bg,
    color: style.text
  }
})
</script>

<style scoped>
.difficulty-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
}
</style>