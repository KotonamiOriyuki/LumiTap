<!--Version 1.0-->
<!--Created: Dec 14, 18:00-->
<template>
  <el-dialog v-model="visible" title="Upload Beatmap" width="600px" :show-close="true" @close="handleClose">
    <el-form :model="form" label-position="top">
      <el-form-item label="Song Title">
        <el-input v-model="form.title" placeholder="Enter song title" />
      </el-form-item>
      <el-form-item label="Artist">
        <el-input v-model="form.artist" placeholder="Enter artist name" />
      </el-form-item>
      <el-form-item label="BPM">
        <el-input-number v-model="form.bpm" :min="1" :max="999" />
      </el-form-item>
      <el-form-item label="Background Image">
        <el-upload
          :auto-upload="false"
          :limit="1"
          accept="image/*"
          :on-change="handleBgChange"
        >
          <el-button>Select Background</el-button>
        </el-upload>
        <span v-if="form.background" class="file-name">{{ form.background.name }}</span>
      </el-form-item>
      <el-form-item label="Audio File (MP3)">
        <el-upload
          :auto-upload="false"
          :limit="1"
          accept="audio/*"
          :on-change="handleAudioChange"
        >
          <el-button>Select Audio</el-button>
        </el-upload>
        <span v-if="form.audio" class="file-name">{{ form.audio.name }}</span>
      </el-form-item>
      <el-divider>Difficulties</el-divider>
      <div v-for="(diff, index) in form.difficulties" :key="index" class="difficulty-row">
        <el-input v-model="diff.name" placeholder="Difficulty Name" style="width: 150px" />
        <el-input-number v-model="diff.level" :min="0" :max="11" :precision="1" :step="0.1" />
        <el-upload
          :auto-upload="false"
          :limit="1"
          accept=".json"
          :on-change="(file) => handleChartChange(file, index)"
        >
          <el-button size="small">Chart JSON</el-button>
        </el-upload>
        <span v-if="diff.chart" class="file-name">{{ diff.chart.name }}</span>
        <el-button type="danger" size="small" @click="removeDifficulty(index)" v-if="form.difficulties.length > 1">Remove</el-button>
      </div>
      <el-button @click="addDifficulty" style="margin-top: 10px">Add Difficulty</el-button>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">Cancel</el-button>
      <el-button type="primary" @click="handleUpload" :loading="loading">Upload</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../utils/api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const loading = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = ref({
  title: '',
  artist: '',
  bpm: 120,
  background: null,
  audio: null,
  difficulties: [{ name: 'Easy', level: 2, chart: null, chartData: null }]
})

const handleBgChange = (file) => {
  form.value.background = file.raw
}

const handleAudioChange = (file) => {
  form.value.audio = file.raw
}

const handleChartChange = async (file, index) => {
  form.value.difficulties[index].chart = file.raw
  const text = await file.raw.text()
  form.value.difficulties[index].chartData = JSON.parse(text)
}

const addDifficulty = () => {
  form.value.difficulties.push({ name: '', level: 5, chart: null, chartData: null })
}

const removeDifficulty = (index) => {
  form.value.difficulties.splice(index, 1)
}

const handleUpload = async () => {
  if (!form.value.title || !form.value.artist || !form.value.background || !form.value.audio) {
    ElMessage.error('Please fill in all required fields')
    return
  }

  for (const diff of form.value.difficulties) {
    if (!diff.name || !diff.chartData) {
      ElMessage.error('Please complete all difficulty information')
      return
    }
  }

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('artist', form.value.artist)
    formData.append('bpm', form.value.bpm)
    formData.append('background', form.value.background)
    formData.append('audio', form.value.audio)

    const difficulties = form.value.difficulties.map(d => ({
      name: d.name,
      level: d.level,
      chart_data: d.chartData
    }))
    formData.append('difficulties', JSON.stringify(difficulties))

    await api.post('/beatmaps/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success('Beatmap uploaded successfully')
    visible.value = false
    handleClose()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Upload failed')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  form.value = {
    title: '',
    artist: '',
    bpm: 120,
    background: null,
    audio: null,
    difficulties: [{ name: 'Easy', level: 2, chart: null, chartData: null }]
  }
}
</script>

<style scoped>
.difficulty-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.file-name {
  font-size: 12px;
  color: #aaa;
  margin-left: 10px;
}
</style>