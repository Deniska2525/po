import api from './api'

class AdminService {
  async getUsers(params = {}) {
    const query = new URLSearchParams(params).toString()
    const { data } = await api.get(`/admin/users?${query}`)
    return data
  }
  
  async updateUserRole(userId, role) {
    const { data } = await api.put(`/admin/users/${userId}/role`, { new_role: role })
    return data
  }
  
  async deleteUser(userId) {
    const { data } = await api.delete(`/admin/users/${userId}`)
    return data
  }
  
  async getProducts(params = {}) {
    const query = new URLSearchParams(params).toString()
    const { data } = await api.get(`/admin/products?${query}`)
    return data
  }
  
  async toggleProductStatus(productId) {
    const { data } = await api.put(`/admin/products/${productId}/toggle`)
    return data
  }
  
  async getCategories() {
    const { data } = await api.get('/admin/categories')
    return data
  }
  
  async createCategory(categoryData) {
    const { data } = await api.post('/admin/categories', categoryData)
    return data
  }
  
  async deleteCategory(categoryId) {
    const { data } = await api.delete(`/admin/categories/${categoryId}`)
    return data
  }
  
  async getDashboardStats() {
    const { data } = await api.get('/admin/dashboard')
    return data
  }
}

export default new AdminService()