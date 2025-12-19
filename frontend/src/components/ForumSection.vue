<!--Created: Dec 19 15:00-->
<!--Ver 1.0-->
<!--Display items of all subforums-->
<template>
  <div class="forum-section">
    <h2 class="section-title">{{ title }}</h2>
    <div class="subforums-container">
      <SubforumItem
          v-for="subforum in subforums"
          :key="subforum.id"
          :subforum="subforum"
      />
    </div>
  </div>
</template>

<script setup>
import SubforumItem from './SubforumItem.vue'

defineProps({
  title: String,
  subforums: Array
})
</script>

<style scoped>
.forum-section {
  margin-bottom: 30px;
}

.section-title {
  color: #00d4ff;
  font-size: 22px;
  margin-bottom: 15px;
  font-weight: bold;
}

.subforums-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
</style>