import { defineStore } from 'pinia'
import api from '../services/api'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    myProducts: [],
    searchResults: [],
    categories: [],
    loading: false
  }),
  
  actions: {
    async fetchAllProducts() {
      this.loading = true
      try {
        const { data } = await api.get('/products/')
        this.products = data
      } finally {
        this.loading = false
      }
    },
    
    async fetchMyProducts() {
      this.loading = true
      try {
        const { data } = await api.get('/products/my')
        this.myProducts = data
      } finally {
        this.loading = false
      }
    },
    
    async createProduct(productData) {
      try {
        const { data } = await api.post('/products/', productData)
        this.myProducts.push(data)
        return { success: true, data }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail }
      }
    },
    
    async updateProduct(productId, productData) {
      try {
        const { data } = await api.put(`/products/${productId}`, productData)
        const index = this.myProducts.findIndex(p => p.id === productId)
        if (index !== -1) this.myProducts[index] = data
        return { success: true, data }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail }
      }
    },
    
    async deleteProduct(productId) {
      try {
        await api.delete(`/products/${productId}`)
        this.myProducts = this.myProducts.filter(p => p.id !== productId)
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail }
      }
    },
    
    async searchProducts(query, filters = {}) {
      this.loading = true
      try {
        const params = { q: query, ...filters }
        const { data } = await api.get('/search/products', { params })
        this.searchResults = data
      } finally {
        this.loading = false
      }
    },
    
    async fetchCategories() {
      try {
        const { data } = await api.get('/search/categories')
        this.categories = data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }
  }
})