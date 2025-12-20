<!--Created: Dec 19, 16:00-->
<!--Ver 1.0-->
<!--Display item of a subforum with statistics-->
<template>
  <div class="subforum-item" @click="goToSubforum">
    <div class="icon-box">
      {{ getInitial(subforum.name) }}
    </div>
    <div class="info">
      <div class="name">{{ subforum.name }}</div>
      <div class="desc">{{ subforum.description }}</div>
      <div class="stats">
        <span>{{ subforum.thread_count || 0 }} Threads</span>
        <span>{{ subforum.post_count || 0 }} Posts</span>
      </div>
    </div>
    <div class="arrow">›</div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  subforum: { type: Object, required: true }
})

const router = useRouter()

const getInitial = (name) => {
  return name ? name.charAt(0).toUpperCase() : '?'
}

const goToSubforum = () => {
  const id = props.subforum.id || props.subforum._id
  if (id) {
    router.push(`/forum/subforum/${id}`)
  }
}
</script>

<style scoped>
.subforum-item {
  display: flex;
  align-items: center;
  background: #2a2a2a;
  border-radius: 8px;
  padding: 15px;
  gap: 15px;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.subforum-item:hover {
  background: #333;
  transform: translateX(4px);
}

.icon-box {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  flex-shrink: 0;
}

.info {
  flex: 1;
  min-width: 0;
}

.name {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 4px;
}

.desc {
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stats {
  font-size: 12px;
  color: #666;
  display: flex;
  gap: 12px;
}

.arrow {
  font-size: 24px;
  color: #555;
}
</style>