<!--Created: Dec 19, 18:30-->
<!--Ver 1.0-->
<!--Display all threads with managements-->
<template>
  <div class="subforum-page">
    <div class="container">
      <div class="top-bar">
        <button class="back-btn" @click="$router.push('/forum')">← Back</button>
      </div>

      <div class="header">
        <div>
          <h1>{{ info?.name || 'Loading...' }}</h1>
          <p>{{ info?.description }}</p>
        </div>
        <button class="new-btn" @click="showDialog = true">+ New Thread</button>
      </div>

      <div v-if="loading" class="status">Loading...</div>
      <div v-else-if="threads.length === 0" class="status">No threads yet.</div>

      <div v-else class="list">
        <div
            v-for="t in threads"
            :key="t.id"
            class="thread-row"
            @click="$router.push(`/forum/thread/${t.id}`)"
        >
          <div class="avatar-box">
            <img v-if="t.author_avatar" :src="t.author_avatar" />
            <div v-else class="avatar-ph">{{ t.author_name?.charAt(0) || '?' }}</div>
          </div>
          <div class="thread-info">
            <div class="title">{{ t.title }}</div>
            <div class="meta">by {{ t.author_name }} · {{ fmtDate(t.created_at) }}</div>
          </div>
          <div class="replies">
            <div class="num">{{ t.reply_count }}</div>
            <div class="label">replies</div>
          </div>
        </div>
      </div>

      <div v-if="showDialog" class="overlay" @click.self="showDialog = false">
        <div class="dialog">
          <div class="dialog-head">
            <h3>New Thread</h3>
            <button @click="showDialog = false">×</button>
          </div>
          <div class="dialog-body">
            <label>Title</label>
            <input v-model="form.title" placeholder="Thread title" />
            <label>Content</label>
            <textarea v-model="form.content" rows="5" placeholder="Write content..."></textarea>
          </div>
          <div class="dialog-foot">
            <button class="cancel" @click="showDialog = false">Cancel</button>
            <button class="submit" @click="submit" :disabled="posting">
              {{ posting ? 'Posting...' : 'Post' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'

const route = useRoute()
const info = ref(null)
const threads = ref([])
const loading = ref(true)
const showDialog = ref(false)
const posting = ref(false)
const form = ref({ title: '', content: '' })

const fmtDate = (ts) => {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleDateString()
}

const load = async () => {
  loading.value = true
  try {
    const res = await api.get(`/forum/subforum/${route.params.id}/threads`)
    info.value = res.data.subforum
    threads.value = res.data.threads || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const submit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  posting.value = true
  try {
    await api.post(`/forum/subforum/${route.params.id}/threads`, form.value)
    showDialog.value = false
    form.value = { title: '', content: '' }
    await load()
  } catch (e) {
    alert('Failed. Please login first.')
  } finally {
    posting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.subforum-page {
  padding: 80px 20px 40px;
  min-height: 100vh;
  background: #1a1a1a;
}
.container { max-width: 900px; margin: 0 auto; }
.top-bar { margin-bottom: 20px; }
.back-btn {
  background: transparent;
  border: 1px solid #444;
  color: #aaa;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
.back-btn:hover { border-color: #00d4ff; color: #00d4ff; }
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 25px;
}
.header h1 { font-size: 24px; color: #fff; margin-bottom: 5px; }
.header p { font-size: 14px; color: #888; }
.new-btn {
  background: #00d4ff;
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.status { text-align: center; color: #888; padding: 60px; }
.list { display: flex; flex-direction: column; gap: 10px; }
.thread-row {
  display: flex;
  align-items: center;
  background: #2a2a2a;
  border-radius: 8px;
  padding: 15px;
  gap: 15px;
  cursor: pointer;
}
.thread-row:hover { background: #333; }
.avatar-box img { width: 45px; height: 45px; border-radius: 50%; }
.avatar-ph {
  width: 45px;
  height: 45px;
  background: #444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #00d4ff;
}
.thread-info { flex: 1; min-width: 0; }
.title { font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 5px; }
.meta { font-size: 12px; color: #888; }
.replies { text-align: center; min-width: 60px; }
.num { font-size: 20px; font-weight: bold; color: #00d4ff; }
.label { font-size: 11px; color: #666; }

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog {
  background: #2a2a2a;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
}
.dialog-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #3a3a3a;
}
.dialog-head h3 { color: #fff; margin: 0; }
.dialog-head button { background: none; border: none; color: #888; font-size: 24px; cursor: pointer; }
.dialog-body { padding: 20px; }
.dialog-body label { display: block; color: #aaa; margin-bottom: 8px; font-size: 14px; }
.dialog-body input, .dialog-body textarea {
  width: 100%;
  background: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 6px;
  padding: 12px;
  color: #fff;
  margin-bottom: 15px;
  box-sizing: border-box;
}
.dialog-body textarea { resize: vertical; min-height: 100px; }
.dialog-foot {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #3a3a3a;
}
.cancel { background: #3a3a3a; color: #fff; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
.submit { background: #00d4ff; color: #000; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.submit:disabled { opacity: 0.5; }
</style>