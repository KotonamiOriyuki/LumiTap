<!--Created: Dec 19, 20:00-->
<!--Ver 1.0-->
<!--Display all replies of a thread with reply function-->
<template>
  <div class="thread-page">
    <div class="container">
      <div class="top-bar">
        <button class="back-btn" @click="goBack">← Back</button>
      </div>

      <div v-if="loading" class="status">Loading...</div>

      <template v-else-if="thread">
        <h1 class="thread-title">{{ thread.title }}</h1>

        <div class="post main-post">
          <div class="post-left clickable" @click="goToProfile(thread.author_id)">
            <div class="avatar">
              <img v-if="thread.author_avatar" :src="thread.author_avatar" />
              <div v-else class="avatar-ph">{{ thread.author_name?.charAt(0) || '?' }}</div>
            </div>
            <div class="author">{{ thread.author_name }}</div>
          </div>
          <div class="post-right">
            <div class="content">{{ thread.content }}</div>
            <div class="post-footer">
              <div class="time">{{ fmtDate(thread.created_at) }}</div>
              <div v-if="isOwner(thread.author_id) || isAdmin()" class="delete-btn" @click="deleteThread">🗑️</div>
            </div>
          </div>
        </div>

        <div class="replies-section">
          <h3>Replies ({{ posts.length }})</h3>
          <div v-if="posts.length === 0" class="no-replies">No replies yet.</div>
          <div v-for="p in posts" :key="p.id" class="post">
            <div class="post-left clickable" @click="goToProfile(p.author_id)">
              <div class="avatar small">
                <img v-if="p.author_avatar" :src="p.author_avatar" />
                <div v-else class="avatar-ph">{{ p.author_name?.charAt(0) || '?' }}</div>
              </div>
              <div class="author">{{ p.author_name }}</div>
            </div>
            <div class="post-right">
              <div class="content">{{ p.content }}</div>
              <div class="post-footer">
                <div class="time">{{ fmtDate(p.created_at) }}</div>
                <div v-if="isOwner(p.author_id) || isAdmin()" class="delete-btn" @click="deleteReply(p.id)">🗑️</div>
              </div>
            </div>
          </div>
        </div>

        <div class="reply-box">
          <h3>Post a Reply</h3>
          <textarea v-model="replyText" rows="4" placeholder="Write your reply..."></textarea>
          <div class="actions">
            <button @click="submitReply" :disabled="posting || !replyText.trim()">
              {{ posting ? 'Posting...' : 'Post Reply' }}
            </button>
          </div>
        </div>
      </template>

      <div v-else class="status">Thread not found.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const thread = ref(null)
const posts = ref([])
const loading = ref(true)
const replyText = ref('')
const posting = ref(false)

const isOwner = (authorId) => {
  return userStore.isAuthenticated && userStore.user?.uid === authorId
}

const isAdmin = () => {
  return userStore.user.flag === "admin"
}

const fmtDate = (ts) => {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleString()
}

const goBack = () => {
  if (thread.value?.subforum_id) {
    router.push(`/forum/subforum/${thread.value.subforum_id}`)
  } else {
    router.push('/forum')
  }
}

const goToProfile = (userId) => {
  if (userId) {
    router.push(`/profile/${userId}`)
  }
}

const load = async () => {
  loading.value = true
  try {
    const res = await api.get(`/forum/thread/${route.params.id}`)
    thread.value = res.data.thread
    posts.value = res.data.posts || []
  } catch (e) {
    thread.value = null
  } finally {
    loading.value = false
  }
}

const submitReply = async () => {
  if (!replyText.value.trim()) return
  posting.value = true
  try {
    await api.post(`/forum/thread/${route.params.id}/reply`, { content: replyText.value })
    replyText.value = ''
    await load()
  } catch (e) {
    alert('Failed. Please login first.')
  } finally {
    posting.value = false
  }
}

const deleteThread = async () => {
  if (!confirm('Are you sure you want to delete this thread? All replies will be removed.')) return
  try {
    await api.delete(`/forum/thread/${route.params.id}`)
    goBack()
  } catch (e) {
    alert('Failed to delete thread.')
  }
}

const deleteReply = async (postId) => {
  if (!confirm('Are you sure you want to delete this reply?')) return
  try {
    await api.delete(`/forum/post/${postId}`)
    await load()
  } catch (e) {
    alert(e)
  }
}

onMounted(load)
</script>

<style scoped>
.post-left.clickable {
  cursor: pointer;
  transition: opacity 0.2s;
}
.post-left.clickable:hover {
  opacity: 0.8;
}

.thread-page {
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
.thread-title { font-size: 26px; color: #fff; margin-bottom: 25px; }
.status { text-align: center; color: #888; padding: 60px; }

.post {
  display: flex;
  background: #2a2a2a;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 15px;
  gap: 20px;
}
.main-post { border-left: 4px solid #00d4ff; }
.post-left { width: 100px; text-align: center; flex-shrink: 0; }
.avatar img { width: 50px; height: 50px; border-radius: 50%; }
.avatar.small img { width: 40px; height: 40px; }
.avatar-ph {
  width: 50px;
  height: 50px;
  background: #3a3a3a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #00d4ff;
  margin: 0 auto;
}
.avatar.small .avatar-ph { width: 40px; height: 40px; font-size: 16px; }
.author { font-size: 14px; color: #00d4ff; margin-top: 8px; font-weight: bold; }
.post-right { flex: 1; display: flex; flex-direction: column; }
.content { color: #ddd; font-size: 15px; line-height: 1.7; white-space: pre-wrap; flex: 1; }
.post-footer {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.time { font-size: 12px; color: #666; }
.delete-btn {
  cursor: pointer;
  font-size: 16px;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.delete-btn:hover { opacity: 1; }

.replies-section { margin-top: 40px; }
.replies-section h3 { color: #fff; margin-bottom: 20px; }
.no-replies { text-align: center; color: #666; padding: 40px; background: #2a2a2a; border-radius: 10px; }

.reply-box {
  margin-top: 40px;
  background: #2a2a2a;
  border-radius: 10px;
  padding: 25px;
}
.reply-box h3 { color: #fff; margin-bottom: 15px; }
.reply-box textarea {
  width: 100%;
  background: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 8px;
  padding: 15px;
  color: #fff;
  font-size: 14px;
  resize: vertical;
  min-height: 100px;
  box-sizing: border-box;
}
.reply-box textarea:focus {
  outline: none;
  border-color: #00d4ff;
}
.actions {
  margin-top: 15px;
  text-align: right;
}
.actions button {
  background: #00d4ff;
  color: #000;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
}
.actions button:hover {
  background: #00b8e6;
}
.actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>