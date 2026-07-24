import { defineStore } from 'pinia'
import api from '../services/api'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    items: [],
    loaded: false,
    loading: false
  }),

  getters: {
    count: (state) => state.items.length,
    favoriteIds: (state) => new Set(state.items.map(p => p.id)),
    isFavorite: (state) => (productId) => state.items.some(p => p.id === productId)
  },

  actions: {
    async fetchFavorites() {
      this.loading = true
      try {
        const { data } = await api.get('/favorites/')
        this.items = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching favorites:', error)
      } finally {
        this.loading = false
      }
    },

    async toggleFavorite(product) {
      const exists = this.items.some(p => p.id === product.id)
      try {
        if (exists) {
          await api.delete(`/favorites/${product.id}`)
          this.items = this.items.filter(p => p.id !== product.id)
        } else {
          await api.post(`/favorites/${product.id}`)
          this.items.push(product)
        }
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail }
      }
    },

    reset() {
      this.items = []
      this.loaded = false
    }
  }
})
