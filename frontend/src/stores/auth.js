import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  }),
  
  getters: {
    welcomeMessage: (state) => {
      if (state.user) {
        return `Приветствую, ${state.user.full_name || state.user.username}!`
      }
      return ''
    },
    userRole: (state) => state.user?.role,
    isDeveloper: (state) => state.user?.role === 'developer',
    isManager: (state) => state.user?.role === 'manager',
    isSuperuser: (state) => state.user?.role === 'superuser'
  },
  
  actions: {
    async login(username, password) {
      try {
        const { data } = await api.post('/users/login', { username, password })
        this.token = data.access_token
        localStorage.setItem('token', this.token)
        this.isAuthenticated = true
        await this.fetchUser()
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Ошибка входа' }
      }
    },
    
    async register(userData) {
      try {
        await api.post('/users/register', userData)
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Ошибка регистрации' }
      }
    },
    
    async fetchUser() {
      try {
        const { data } = await api.get('/users/me')
        this.user = data
        return data
      } catch {
        this.logout()
        throw new Error('Session expired')
      }
    },
    
    async updateUser(userData) {
      try {
        const { data } = await api.put('/users/me', userData)
        this.user = data
        return { success: true, data }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail }
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
    }
  }
})