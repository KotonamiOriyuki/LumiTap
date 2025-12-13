<template>
  <el-dialog v-model="visible" title="Login" width="400px" :show-close="true" @close="handleClose">
    <el-form :model="form" label-position="top">
      <el-form-item label="Username">
        <el-input v-model="form.username" placeholder="Enter username" />
      </el-form-item>
      <el-form-item label="Password">
        <el-input v-model="form.password" type="password" placeholder="Enter password" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <span class="switch-link" @click="switchToRegister">Don't have an account? Register</span>
        <el-button type="primary" @click="handleLogin" :loading="loading">Login</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'switch-to-register'])

const userStore = useUserStore()
const loading = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.error('Please fill in all fields')
    return
  }

  loading.value = true
  try {
    await userStore.login(form.value.username, form.value.password)
    ElMessage.success('Login successful')
    visible.value = false
    form.value = { username: '', password: '' }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Login failed')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  form.value = { username: '', password: '' }
}

const switchToRegister = () => {
  emit('switch-to-register')
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.switch-link {
  color: #00d4ff;
  cursor: pointer;
  font-size: 13px;
}

.switch-link:hover {
  text-decoration: underline;
}
</style>