import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    const isAuthenticated = ref(false)

    const checkAuth = async () => {
        try {
            const res = await api.get('/users/check')
            if (res.data.authenticated) {
                user.value = res.data.user
                isAuthenticated.value = true
            } else {
                user.value = null
                isAuthenticated.value = false
            }
        } catch (e) {
            user.value = null
            isAuthenticated.value = false
        }
    }

    const login = async (username, password) => {
        const res = await api.post('/auth/login', { username, password })
        user.value = res.data
        isAuthenticated.value = true
        return res.data
    }

    const register = async (username, password) => {
        const res = await api.post('/auth/register', { username, password })
        user.value = res.data
        isAuthenticated.value = true
        return res.data
    }

    // Jiarui Li: logout function and user update function
    const logout = async () => {
        await api.post('/auth/logout')
        user.value = null
        isAuthenticated.value = false
    }

    const updateUser = (data) => {
        if (user.value) {
            Object.assign(user.value, data)
        }
    }

    return { user, isAuthenticated, checkAuth, login, register, logout, updateUser }
})