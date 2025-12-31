<!--Ver 1.1-->
<!--Changelog: Dec 31, 21:00, adapt to the mobile client and modified the layout-->
<template>
  <div class="profile-view" v-if="profile">
    <div class="profile-container">
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar-wrapper" @click="handleAvatarClick">
            <img :src="profile.avatar || defaultAvatar" alt="avatar" />
            <div class="avatar-overlay" v-if="isOwnProfile && isEditing">
              <span>Change</span>
            </div>
          </div>
          <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleAvatarChange"
          />
        </div>
        <div class="profile-main-info">
          <div class="username-row">
            <input
                v-if="isEditing"
                v-model="editForm.username"
                class="username-input"
                placeholder="Username"
            />
            <h1 v-else class="username">{{ profile.username }}</h1>
          </div>
          <div class="stats-row">
            <div class="ep-group">
              <div class="ep-row">
                <span class="ep-label">EP:</span>
                <span class="ep-value consolas" :style="{ color: epColor }" :class="{ 'high-ep': highEP }">
                  {{ profile.ep.toFixed(2) }}
                </span>
              </div>
              <div class="ep-hint">*EP: Estimated Performance</div>
            </div>
            <div class="rank-group">
              <span class="rank-label">Global Rank</span>
              <div class="rank-value">#{{ profile.rank }}</div>
            </div>
          </div>
        </div>
<!--        Chenxi Liu: Layout adjustment     -->
        <div class="profile-actions">
          <button v-if="isOwnProfile && !isEditing" class="edit-btn" @click="startEdit">Edit Profile</button>
          <button v-if="isOwnProfile && !isEditing" class="logout-btn" @click="handleLogout">Logout</button>
          <button v-if="isOwnProfile && isEditing" class="save-btn" @click="saveEdit">Save Changes</button>
          <button v-if="isOwnProfile && isEditing" class="cancel-btn" @click="cancelEdit">Cancel</button>
        </div>
      </div>

      <h2 class="scores-title">Best Scores</h2>
      <div class="scores-card">
        <ScoreCard
            v-for="(score, index) in scores"
            :key="score.scid"
            :score="score"
            :index="index"
        />
        <div v-if="scores.length === 0" class="no-scores">
          No scores yet
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getEPColor, isHighEP } from '../utils/scoring'
import api from '../utils/api'
import ScoreCard from '../components/ScoreCard.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const profile = ref(null)
const scores = ref([])
const isEditing = ref(false)
const editForm = ref({ username: '' })
const avatarInput = ref(null)

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23333" width="100" height="100"/><circle fill="%23666" cx="50" cy="35" r="20"/><ellipse fill="%23666" cx="50" cy="85" rx="35" ry="25"/></svg>'

const isOwnProfile = computed(() => {
  if (route.name === 'me') return true
  if (!userStore.user) return false
  return userStore.user.uid === route.params.uid
})

const epColor = computed(() => {
  if (!profile.value) return '#ffffff'
  return getEPColor(profile.value.ep)
})

const highEP = computed(() => {
  if (!profile.value) return false
  return isHighEP(profile.value.ep)
})

const loadProfile = async () => {
  try {
    let uid
    if (route.name === 'me') {
      if (!userStore.isAuthenticated) {
        router.push('/')
        return
      }
      uid = userStore.user.uid
    } else {
      uid = route.params.uid
    }

    const res = await api.get(`/users/${uid}`)
    profile.value = res.data

    const scoresRes = await api.get(`/users/${uid}/scores`)
    scores.value = scoresRes.data
  } catch (e) {
    console.error('Failed to load profile')
    ElMessage.error('Failed to load profile')
  }
}

const startEdit = () => {
  editForm.value.username = profile.value.username
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  editForm.value = { username: '' }
}

const saveEdit = async () => {
  try {
    if (editForm.value.username && editForm.value.username !== profile.value.username) {
      await api.put('/users/me', { username: editForm.value.username })
      profile.value.username = editForm.value.username
      userStore.updateUser({ username: editForm.value.username })
    }
    isEditing.value = false
    ElMessage.success('Profile updated')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Failed to update profile')
  }
}

const handleAvatarClick = () => {
  if (isOwnProfile.value && isEditing.value) {
    avatarInput.value.click()
  }
}

const handleAvatarChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await api.post('/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    profile.value.avatar = res.data.avatar
    userStore.updateUser({ avatar: res.data.avatar })
    ElMessage.success('Avatar updated')
  } catch (e) {
    ElMessage.error('Failed to upload avatar')
  }
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/')
    ElMessage.success('Logged out')
  } catch (e) {
    ElMessage.error('Failed to logout')
  }
}

onMounted(() => {
  loadProfile()
})

watch(() => route.params.uid, () => {
  loadProfile()
})

watch(() => route.name, () => {
  if (route.name === 'me' || route.name === 'profile') {
    loadProfile()
  }
})
</script>

<style scoped>
.profile-view {
  min-height: calc(100vh - 50px);
  padding: 30px;
}

.profile-container {
  max-width: 900px;
  margin: 0 auto;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 30px;
  background-color: #2a2a2a;
  border-radius: 12px;
  gap: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.avatar-section {
  flex-shrink: 0;
}

.avatar-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  border: 3px solid #3a3a3a;
}

.avatar-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 14px;
}

.profile-main-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.username-row {
  display: flex;
  align-items: center;
}

.username {
  font-size: 28px;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
}

.username-input {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
  background-color: #3a3a3a;
  border: 1px solid #00d4ff;
  border-radius: 4px;
  padding: 5px 12px;
  outline: none;
  width: 100%;
}

.stats-row {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.ep-group, .rank-group {
  display: flex;
  flex-direction: column;
}

.ep-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ep-label, .rank-label {
  font-size: 14px;
  color: #aaaaaa;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.ep-value {
  font-size: 24px;
  font-weight: bold;
}

.ep-value.high-ep {
  text-shadow: 0 0 10px currentColor, 0 0 20px currentColor;
}

.ep-hint {
  font-size: 11px;
  color: #666666;
  margin-top: 2px;
}

.rank-value {
  font-size: 24px;
  font-weight: bold;
  color: #00d4ff;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
}

.logout-btn, .edit-btn, .cancel-btn, .save-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  min-width: 120px;
  text-align: center;
}

.logout-btn {
  background-color: transparent;
  color: #f44336;
  border: 1px solid #f44336;
}

.logout-btn:hover {
  background-color: #f44336;
  color: #ffffff;
}

.edit-btn {
  background-color: #00d4ff;
  color: #1a1a1a;
}

.edit-btn:hover {
  background-color: #00b8d9;
  transform: translateY(-1px);
}

.cancel-btn {
  background-color: #444444;
  color: #ffffff;
}

.save-btn {
  background-color: #4caf50;
  color: #ffffff;
}

.scores-title {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  margin: 30px 0 15px 10px;
}

.scores-card {
  background-color: #3a3a3a;
  border-radius: 8px;
  overflow: hidden;
}

.no-scores {
  padding: 40px;
  text-align: center;
  color: #666666;
}

@media (max-width: 768px) {
  .profile-view {
    padding: 15px;
  }

  .profile-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 25px 15px;
    gap: 20px;
  }

  .username-row {
    justify-content: center;
  }

  .username {
    text-align: center;
  }

  .stats-row {
    justify-content: center;
    gap: 30px;
  }

  .profile-actions {
    width: 100%;
    flex-direction: row;
    justify-content: center;
  }

  .logout-btn, .edit-btn, .cancel-btn, .save-btn {
    flex: 1;
    min-width: 0;
  }
}
</style>