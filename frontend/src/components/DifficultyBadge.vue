<!--Created: Dec 14 20:00-->
<!--Ver 1.1-->
<!--Display badges for each difficulties-->
<!--Changelog: Hidden Difficulty name when space is insufficient, Dec 30, 18:00-->
<template>
<!--  Yiwen Wang: Judge the width  -->
  <div class="difficulty-badge" :style="badgeStyle" :class="{ 'mobile-collapsed': !selected, 'large': isLarge }">
    <span class="badge-name">{{ name }}</span>
    <span class="badge-level">{{ level }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getDifficultyStyle } from '../utils/scoring'

const props = defineProps({
  name: String,
  level: Number,
  selected: {
    type: Boolean,
    default: false
  },
  isLarge: {
    type: Boolean,
    default: false
  }
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
  display: flex;
  gap: 4px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.difficulty-badge.large {
  padding: 8px 16px;
  font-size: 13px;
}

@media (max-width: 768px) {
  .mobile-collapsed .badge-name {
    display: none;
  }

  .difficulty-badge {
    padding: 4px 8px;
    justify-content: center;
    min-width: 28px;
  }

  .difficulty-badge.large {
    padding: 8px 12px;
  }

  .difficulty-badge:not(.mobile-collapsed) .badge-name {
    display: inline;
  }

  .difficulty-badge:not(.mobile-collapsed) {
    padding: 4px 12px;
  }

  .difficulty-badge.large:not(.mobile-collapsed) {
    padding: 8px 16px;
  }
}
</style>