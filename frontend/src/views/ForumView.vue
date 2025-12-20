<!--Created: Dec 19, 17:00-->
<!--Ver 1.0-->
<!--Display all subforum items-->
<template>
  <div class="forum-page">
    <div class="container">
      <div class="page-header">
        <h1>Forum</h1>
        <button class="init-btn" @click="initForum" v-if="sections.length === 0">
          Initialize Forum
        </button>
      </div>

      <div v-if="loading" class="loading">Loading...</div>

      <div v-else-if="sections.length === 0" class="empty">
        <p>No forum sections found.</p>
        <p>Click "Initialize Forum" to create default sections.</p>
      </div>

      <div v-else class="sections-list">
        <div v-for="section in sections" :key="section.id" class="section">
          <div class="section-header">
            <h2>{{ section.name }}</h2>
            <span class="section-desc">{{ section.description }}</span>
          </div>
          <div class="subforums-list">
            <SubforumItem
                v-for="sf in section.subforums"
                :key="sf.id"
                :subforum="sf"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import SubforumItem from '../components/SubforumItem.vue'

const sections = ref([])
const loading = ref(true)

const fetchSections = async () => {
  loading.value = true
  try {
    const res = await api.get('/forum/sections')
    sections.value = res.data || []
  } catch (e) {
    console.error('Failed to load forum sections:', e)
    sections.value = []
  } finally {
    loading.value = false
  }
}

const initForum = async () => {
  try {
    await api.post('/forum/init')
    await fetchSections()
  } catch (e) {
    console.error('Failed to initialize forum:', e)
  }
}

onMounted(fetchSections)
</script>

<style scoped>
.forum-page {
  padding: 80px 20px 40px;
  min-height: 100vh;
  background-color: #1a1a1a;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #ffffff;
}

.init-btn {
  background-color: #00d4ff;
  color: #000000;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.init-btn:hover {
  background-color: #00b8e6;
}

.loading, .empty {
  text-align: center;
  color: #888888;
  padding: 60px 20px;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section-header {
  margin-bottom: 15px;
}

.section-header h2 {
  font-size: 20px;
  color: #00d4ff;
  margin-bottom: 5px;
}

.section-desc {
  font-size: 13px;
  color: #777777;
}

.subforums-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>