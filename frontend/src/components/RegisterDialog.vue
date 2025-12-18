<template>
  <el-dialog v-model="visible" title="Register" width="400px" :show-close="true" @close="handleClose">
    <el-form :model="form" label-position="top">
      <el-form-item label="Username">
        <el-input v-model="form.username" placeholder="Enter username" />
      </el-form-item>
      <el-form-item label="Password">
        <el-input v-model="form.password" type="password" placeholder="Enter password" />
      </el-form-item>
      <el-form-item label="Confirm Password">
        <el-input v-model="form.confirmPassword" type="password" placeholder="Confirm password" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <span class="switch-link" @click="switchToLogin">Already have an account? Login</span>
        <el-button type="primary" @click="handleRegister" :loading="loading">Register</el-button>
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

const emit = defineEmits(['update:modelValue', 'switch-to-login'])

const userStore = useUserStore()
const loading = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  if (!form.value.username || !form.value.password || !form.value.confirmPassword) {
    ElMessage.error('Please fill in all fields')
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error('Passwords do not match')
    return
  }

  loading.value = true
  try {
    await userStore.register(form.value.username, form.value.password)
    ElMessage.success('Registration successful')
    visible.value = false
    form.value = { username: '', password: '', confirmPassword: '' }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  form.value = { username: '', password: '', confirmPassword: '' }
}

const switchToLogin = () => {
  emit('switch-to-login')
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