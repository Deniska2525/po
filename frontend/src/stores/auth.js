import { defineStore } from 'pinia'
import api, { setAccessToken } from '../services/api'
import { useFavoritesStore } from './favorites'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false
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
        setAccessToken(data.access_token)
        this.isAuthenticated = true
        await this.fetchUser()
        await useFavoritesStore().fetchFavorites()
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Ошибка входа' }
      }
    },

    // Восстановление сессии при загрузке приложения: refresh-токен лежит
    // в httpOnly cookie, поэтому просто пробуем обменять его на access-токен.
    async init() {
      try {
        const { data } = await api.post('/users/refresh')
        setAccessToken(data.access_token)
        this.isAuthenticated = true
        await this.fetchUser()
        await useFavoritesStore().fetchFavorites()
      } catch {
        // Нет валидной сессии — остаёмся гостем
        setAccessToken(null)
        this.isAuthenticated = false
      }
    },
    
    async register(userData) {
      try {
        await api.post('/users/register', userData)
        return { success: true }
      } catch (error) {
        const detail = error.response?.data?.detail
        // Ошибки валидации pydantic приходят массивом объектов
        const message = Array.isArray(detail)
          ? detail.map(d => d.msg).join('; ')
          : (detail || 'Ошибка регистрации')
        return { success: false, message }
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
    
    async logout() {
      // Отзываем refresh-токен на сервере и чистим cookie
      try { await api.post('/users/logout') } catch { /* сеть могла отвалиться — всё равно чистим локально */ }
      this.user = null
      this.isAuthenticated = false
      setAccessToken(null)
      // Сбрасываем избранное — это данные конкретного пользователя,
      // им не место в сессии следующего, кто зайдёт с этого браузера.
      useFavoritesStore().reset()
    }
  }
})
